"""
Scheduler service for managing cron jobs and periodic tasks.

This service uses APScheduler to manage scheduled tasks including
stock price checks, alert processing, and system maintenance.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from ..models.config import SchedulerConfig
from ..models.stock import Stock, StockAlert

# Configure logging
logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service for managing scheduled tasks and cron jobs.
    
    This service provides methods for scheduling stock price checks,
    alert processing, and other periodic tasks.
    """
    
    def __init__(self):
        """Initialize the scheduler service."""
        try:
            # Configure job stores and executors
            jobstores = {
                'default': MemoryJobStore()
            }
            
            executors = {
                'default': AsyncIOExecutor()
            }
            
            job_defaults = {
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
            
            # Create scheduler
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # Task callbacks
            self._task_callbacks: Dict[str, Callable] = {}
            
            # Scheduler state
            self._is_running = False
            self._last_check = None
            self._check_count = 0
            
            logger.info("Scheduler service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler service: {str(e)}")
            raise
    
    def register_task_callback(self, task_name: str, callback: Callable):
        """
        Register a callback function for a specific task.
        
        Args:
            task_name: Name of the task
            callback: Callback function to execute
        """
        self._task_callbacks[task_name] = callback
        logger.info(f"Registered callback for task: {task_name}")
    
    async def start(self):
        """Start the scheduler."""
        try:
            if not self._is_running:
                self.scheduler.start()
                self._is_running = True
                logger.info("Scheduler started successfully")
                
                # Schedule default tasks
                await self._schedule_default_tasks()
            else:
                logger.warning("Scheduler is already running")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the scheduler."""
        try:
            if self._is_running:
                self.scheduler.shutdown()
                self._is_running = False
                logger.info("Scheduler stopped successfully")
            else:
                logger.warning("Scheduler is not running")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            raise
    
    async def _schedule_default_tasks(self):
        """Schedule default tasks."""
        try:
            # Schedule stock price check during market hours (9:30 AM - 4:00 PM EST)
            # Market hours: 9:35 AM, 10:30 AM, 12:00 PM, 2:00 PM, 3:55 PM EST
            market_hours_schedule = getattr(settings, 'market_hours_schedule', True)
            
            if market_hours_schedule:
                # Schedule for specific market hours (EST)
                market_times = [
                    {'hour': 9, 'minute': 35},   # 9:35 AM EST
                    {'hour': 10, 'minute': 30},  # 10:30 AM EST  
                    {'hour': 12, 'minute': 0},   # 12:00 PM EST
                    {'hour': 14, 'minute': 0},   # 2:00 PM EST
                    {'hour': 15, 'minute': 55}   # 3:55 PM EST
                ]
                
                for i, time in enumerate(market_times):
                    self.scheduler.add_job(
                        func=self._execute_stock_check,
                        trigger=CronTrigger(hour=time['hour'], minute=time['minute']),
                        id=f'stock_price_check_{i+1}',
                        name=f'Stock Price Check {time["hour"]:02d}:{time["minute"]:02d}',
                        replace_existing=True
                    )
                
                logger.info("Market hours schedule configured: 9:35 AM, 10:30 AM, 12:00 PM, 2:00 PM, 3:55 PM EST")
            else:
                # Fallback to interval-based scheduling
                check_interval = SchedulerConfig.get_check_interval()
                self.scheduler.add_job(
                    func=self._execute_stock_check,
                    trigger=IntervalTrigger(minutes=check_interval),
                    id='stock_price_check',
                    name='Stock Price Check',
                    replace_existing=True
                )
                logger.info(f"Interval-based schedule configured: every {check_interval} minutes")
            
            # Schedule cache cleanup (daily at 2 AM)
            self.scheduler.add_job(
                func=self._execute_cache_cleanup,
                trigger=CronTrigger(hour=2, minute=0),
                id='cache_cleanup',
                name='Cache Cleanup',
                replace_existing=True
            )
            
            # Schedule system health check (every 30 minutes)
            self.scheduler.add_job(
                func=self._execute_health_check,
                trigger=IntervalTrigger(minutes=30),
                id='health_check',
                name='System Health Check',
                replace_existing=True
            )
            
            logger.info("Default tasks scheduled successfully")
            
        except Exception as e:
            logger.error(f"Error scheduling default tasks: {str(e)}")
            raise
    
    async def _execute_stock_check(self):
        """
        Execute stock price check task.
        
        This is the main scheduled task that checks stock prices
        and triggers alerts when thresholds are exceeded.
        """
        try:
            logger.info("Starting scheduled stock price check")
            self._check_count += 1
            self._last_check = datetime.utcnow()
            
            # Execute the stock check callback if registered
            if 'stock_check' in self._task_callbacks:
                callback = self._task_callbacks['stock_check']
                await callback()
            else:
                logger.warning("No stock check callback registered")
            
            logger.info(f"Stock price check completed (check #{self._check_count})")
            
        except Exception as e:
            logger.error(f"Error executing stock check: {str(e)}")
    
    async def _execute_cache_cleanup(self):
        """
        Execute cache cleanup task.
        
        This task cleans up old cached data and temporary files.
        """
        try:
            logger.info("Starting cache cleanup task")
            
            # Execute cache cleanup callback if registered
            if 'cache_cleanup' in self._task_callbacks:
                callback = self._task_callbacks['cache_cleanup']
                await callback()
            else:
                logger.warning("No cache cleanup callback registered")
            
            logger.info("Cache cleanup completed")
            
        except Exception as e:
            logger.error(f"Error executing cache cleanup: {str(e)}")
    
    async def _execute_health_check(self):
        """
        Execute system health check task.
        
        This task checks the health of various system components.
        """
        try:
            logger.info("Starting system health check")
            
            # Execute health check callback if registered
            if 'health_check' in self._task_callbacks:
                callback = self._task_callbacks['health_check']
                await callback()
            else:
                logger.warning("No health check callback registered")
            
            logger.info("System health check completed")
            
        except Exception as e:
            logger.error(f"Error executing health check: {str(e)}")
    
    def schedule_custom_task(self, task_id: str, func: Callable, 
                           trigger_type: str = "interval", **kwargs) -> bool:
        """
        Schedule a custom task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            trigger_type: Type of trigger (interval, cron, date)
            **kwargs: Additional trigger parameters
            
        Returns:
            True if task was scheduled successfully
        """
        try:
            # Create trigger based on type
            if trigger_type == "interval":
                trigger = IntervalTrigger(**kwargs)
            elif trigger_type == "cron":
                trigger = CronTrigger(**kwargs)
            else:
                raise ValueError(f"Unsupported trigger type: {trigger_type}")
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_id,
                name=f"Custom Task: {task_id}",
                replace_existing=True
            )
            
            logger.info(f"Custom task scheduled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling custom task {task_id}: {str(e)}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            True if task was removed successfully
        """
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"Task removed: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing task {task_id}: {str(e)}")
            return False
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of all scheduled tasks.
        
        Returns:
            List of task information dictionaries
        """
        try:
            jobs = self.scheduler.get_jobs()
            task_list = []
            
            for job in jobs:
                task_info = {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                    'func': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
                }
                task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {str(e)}")
            return []
    
    def update_check_interval(self, minutes: int) -> bool:
        """
        Update the stock check interval.
        
        Args:
            minutes: New interval in minutes
            
        Returns:
            True if interval was updated successfully
        """
        try:
            # Remove existing job
            self.scheduler.remove_job('stock_price_check')
            
            # Add new job with updated interval
            self.scheduler.add_job(
                func=self._execute_stock_check,
                trigger=IntervalTrigger(minutes=minutes),
                id='stock_price_check',
                name='Stock Price Check',
                replace_existing=True
            )
            
            logger.info(f"Stock check interval updated to {minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error updating check interval: {str(e)}")
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """
        Pause a scheduled task.
        
        Args:
            task_id: ID of the task to pause
            
        Returns:
            True if task was paused successfully
        """
        try:
            self.scheduler.pause_job(task_id)
            logger.info(f"Task paused: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing task {task_id}: {str(e)}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """
        Resume a paused task.
        
        Args:
            task_id: ID of the task to resume
            
        Returns:
            True if task was resumed successfully
        """
        try:
            self.scheduler.resume_job(task_id)
            logger.info(f"Task resumed: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming task {task_id}: {str(e)}")
            return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get scheduler status information.
        
        Returns:
            Dictionary with scheduler status
        """
        try:
            return {
                'is_running': self._is_running,
                'last_check': self._last_check.isoformat() if self._last_check else None,
                'check_count': self._check_count,
                'scheduled_tasks': len(self.scheduler.get_jobs()),
                'registered_callbacks': len(self._task_callbacks),
                'check_interval_minutes': SchedulerConfig.get_check_interval(),
                'alert_threshold_percent': SchedulerConfig.get_alert_threshold(),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            return {
                'is_running': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def execute_immediate_check(self) -> bool:
        """
        Execute an immediate stock check (outside of schedule).
        
        Returns:
            True if check was executed successfully
        """
        try:
            logger.info("Executing immediate stock check")
            await self._execute_stock_check()
            return True
        except Exception as e:
            logger.error(f"Error executing immediate check: {str(e)}")
            return False
    
    def get_next_run_times(self) -> Dict[str, Optional[str]]:
        """
        Get next run times for all scheduled tasks.
        
        Returns:
            Dictionary mapping task IDs to next run times
        """
        try:
            jobs = self.scheduler.get_jobs()
            next_runs = {}
            
            for job in jobs:
                next_run = job.next_run_time
                next_runs[job.id] = next_run.isoformat() if next_run else None
            
            return next_runs
            
        except Exception as e:
            logger.error(f"Error getting next run times: {str(e)}")
            return {}
