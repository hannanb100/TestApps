#!/usr/bin/env python3
"""
🌐 WEB INTERFACE FOR AGENT TEAM SYSTEM - PROFESSIONAL VERSION
=============================================================

Professional, clean web interface without workflow information,
with Enter key submission and modern styling.
"""

import os
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import threading

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

from agent_system_final import process_user_request

# Global status tracking
current_status = "Ready"
current_task = "Waiting for request"
status_lock = threading.Lock()

def update_status(status, task):
    global current_status, current_task
    with status_lock:
        current_status = status
        current_task = task

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self._create_main_page()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            user_request = parsed_data.get('request', [''])[0]
            
            try:
                update_status("Processing", "Starting AI research workflow...")
                result = process_user_request(user_request)
                
                # Check if there's an error in the result
                if result.get('error'):
                    error_html = self._display_error_info(result)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(error_html.encode('utf-8'))
                    return
                
                update_status("Completed", "Request processed successfully")
                html = self._create_results_page(user_request, result)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                
            except Exception as e:
                update_status("Error", f"Error occurred: {str(e)}")
                error_html = self._create_error_page(str(e))
                
                self.send_response(500)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(error_html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def _create_main_page(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Research Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white; 
            padding: 60px 40px; 
            border-radius: 20px; 
            text-align: center; 
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 6s ease-in-out infinite;
        }
        @keyframes shimmer {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(180deg); }
        }
        .header h1 { 
            font-size: 3.2em; 
            font-weight: 300; 
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }
        .header p { 
            font-size: 1.3em;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }
        .main-content {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .info-section { 
            margin-bottom: 40px;
        }
        .info-section h3 { 
            color: #2c3e50; 
            font-size: 1.4em;
            margin-bottom: 20px;
            font-weight: 600;
            position: relative;
            padding-left: 20px;
        }
        .info-section h3::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            border-radius: 2px;
        }
        .examples-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }
        .example-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .example-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
            border-left-color: #2c3e50;
        }
        .example-card h4 {
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .example-card p {
            color: #6c757d;
            font-size: 0.95em;
            line-height: 1.5;
        }
        .form-section {
            margin-top: 40px;
        }
        .form-group { 
            margin-bottom: 30px;
        }
        label { 
            display: block; 
            margin-bottom: 12px; 
            font-weight: 600; 
            color: #2c3e50; 
            font-size: 1.2em;
        }
        textarea { 
            width: 100%; 
            height: 140px; 
            padding: 20px; 
            border-radius: 12px; 
            border: 2px solid #e1e8ed; 
            font-size: 16px; 
            font-family: inherit; 
            resize: vertical; 
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(5px);
        }
        textarea:focus { 
            outline: none; 
            border-color: #3498db; 
            box-shadow: 0 0 0 4px rgba(52, 152, 219, 0.1); 
            background: rgba(255,255,255,0.95);
        }
        textarea::placeholder {
            color: #95a5a6;
            font-style: italic;
        }
        .submit-btn { 
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%); 
            color: white; 
            border: none; 
            padding: 20px 40px; 
            font-size: 18px; 
            border-radius: 12px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
            width: 100%; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        .submit-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }
        .submit-btn:hover::before {
            left: 100%;
        }
        .submit-btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.2); 
        }
        .submit-btn:active { 
            transform: translateY(-1px); 
        }
        .help-text {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 8px;
            font-style: italic;
        }
        @media (max-width: 768px) {
            .container { padding: 20px 15px; }
            .header { padding: 40px 30px; }
            .header h1 { font-size: 2.5em; }
            .main-content { padding: 30px; }
            .examples-grid { grid-template-columns: 1fr; }
        }
    </style>
    <script>
        // Form submission with Enter key
        document.addEventListener('DOMContentLoaded', function() {
            const textarea = document.getElementById('request');
            const form = document.querySelector('form');
            
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (textarea.value.trim()) {
                        form.submit();
                    }
                }
            });
            
            // Example click handlers
            document.querySelectorAll('.example-card').forEach(card => {
                card.addEventListener('click', function() {
                    const example = this.querySelector('p').textContent;
                    textarea.value = example;
                    textarea.focus();
                });
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 AI Research Assistant</h1>
            <p>Professional research and document creation powered by advanced AI</p>
        </div>
        
        <div class="main-content">
            <div class="info-section">
                <h3>💡 What You Can Request</h3>
                <p>Our AI system specializes in comprehensive research and professional document creation. Click any example below to get started:</p>
                
                <div class="examples-grid">
                    <div class="example-card">
                        <h4>📊 Market Research</h4>
                        <p>Create a comprehensive report on renewable energy trends and market opportunities</p>
                    </div>
                    <div class="example-card">
                        <h4>🔬 Technical Analysis</h4>
                        <p>Analyze the latest developments in quantum computing and their business applications</p>
                    </div>
                    <div class="example-card">
                        <h4>📈 Industry Studies</h4>
                        <p>Compare different approaches to sustainable agriculture and their economic impact</p>
                    </div>
                    <div class="example-card">
                        <h4>📚 Educational Content</h4>
                        <p>Write a comprehensive beginner's guide to machine learning and AI applications</p>
                    </div>
                </div>
            </div>
            
            <div class="form-section">
                <form method="POST" action="/process">
                    <div class="form-group">
                        <label for="request">Describe your research request:</label>
                        <textarea 
                            name="request" 
                            id="request" 
                            placeholder="Enter your detailed request here. Be specific about what you need researched, analyzed, or documented. Press Enter to submit or Shift+Enter for a new line."
                            required
                        ></textarea>
                        <div class="help-text">💡 Tip: The more specific your request, the better the results. Press Enter to submit.</div>
                    </div>
                    <button type="submit" class="submit-btn">
                        Generate Research Report
                    </button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _create_results_page(self, user_request, result):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Research Results - AI Assistant</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .header {{ 
            background: linear-gradient(135deg, #27ae60 0%, #2c3e50 100%);
            color: white; 
            padding: 40px; 
            border-radius: 20px; 
            text-align: center; 
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            font-weight: 300; 
            margin-bottom: 10px;
        }}
        .section {{ 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px; 
            margin: 30px 0; 
            border-radius: 15px; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .section h3 {{ 
            color: #2c3e50; 
            font-size: 1.4em;
            margin-bottom: 20px;
            font-weight: 600;
            position: relative;
            padding-left: 20px;
        }}
        .section h3::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #27ae60, #2c3e50);
            border-radius: 2px;
        }}
        .output {{ 
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
            padding: 25px; 
            border-radius: 12px; 
            white-space: pre-wrap; 
            font-family: 'Georgia', serif; 
            border-left: 4px solid #27ae60;
            max-height: 600px;
            overflow-y: auto;
            line-height: 1.8;
            font-size: 16px;
        }}
        .request-box {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #3498db;
            font-style: italic;
        }}
        .back-btn {{ 
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%); 
            color: white; 
            padding: 18px 35px; 
            text-decoration: none; 
            border-radius: 12px; 
            display: inline-block; 
            margin-top: 30px; 
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .back-btn:hover {{ 
            transform: translateY(-3px); 
            box-shadow: 0 15px 30px rgba(0,0,0,0.2); 
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border-top: 4px solid #3498db;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            display: block;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 20px 15px; }}
            .section {{ padding: 20px; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Research Complete</h1>
            <p>Your AI research assistant has successfully processed your request</p>
        </div>
        
        <div class="section">
            <h3>📋 Your Request</h3>
            <div class="request-box">{user_request}</div>
        </div>
        
        <div class="section">
            <h3>📊 Processing Summary</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-number">{len(set(result.get('supervisor_decisions', [])))}</span>
                    <div class="stat-label">Unique AI Decisions</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{sum(result.get('token_usage', {}).values())}</span>
                    <div class="stat-label">Tokens Processed</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len([k for k, v in result.get('quality_scores', {}).items() if v > 0.6])}</span>
                    <div class="stat-label">High Quality Results</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{result.get('workflow_phase', 'Unknown').title()}</span>
                    <div class="stat-label">Final Status</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>🎯 Final Research Report</h3>
            <div class="output">{result.get('final_output', 'No output generated')}</div>
        </div>
        
        <a href="/" class="back-btn">🔄 New Research Request</a>
    </div>
</body>
</html>"""
        
        return html
    
    def _display_error_info(self, result):
        """Display detailed error information in a user-friendly format"""
        error_details = result.get('error_details', 'Unknown error occurred')
        error_type = result.get('error_type', 'System Error')
        
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Service Temporarily Unavailable</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .error-container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 40px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .error-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        .error-title {{
            color: #e74c3c;
            font-size: 2em;
            margin-bottom: 20px;
            font-weight: 300;
        }}
        .error-message {{
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 1.1em;
            line-height: 1.8;
        }}
        .error-details {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }}
        .error-details h4 {{
            color: #e53e3e;
            margin-bottom: 10px;
        }}
        .suggestions {{
            background: #f0f8ff;
            border: 1px solid #bee3f8;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }}
        .suggestions h4 {{
            color: #3182ce;
            margin-bottom: 15px;
        }}
        .suggestions ul {{
            margin-left: 20px;
        }}
        .suggestions li {{
            margin-bottom: 8px;
            color: #4a5568;
        }}
        .back-btn {{
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 12px;
            display: inline-block;
            margin-top: 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .back-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h1 class="error-title">Service Temporarily Unavailable</h1>
        <p class="error-message">We're experiencing some technical difficulties. This is usually temporary and related to API service limits.</p>
        
        <div class="error-details">
            <h4>Error Details:</h4>
            <p>{error_details}</p>
        </div>
        
        <div class="suggestions">
            <h4>What you can do:</h4>
            <ul>
                <li>Try submitting your request again in a few minutes</li>
                <li>Simplify your request if it's very complex</li>
                <li>Check your internet connection</li>
                <li>Contact support if the problem persists</li>
            </ul>
        </div>
        
        <a href="/" class="back-btn">🔄 Try Again</a>
    </div>
</body>
</html>"""
        
        return error_html
    
    def _create_error_page(self, error_message):
        return self._display_error_info({
            'error_details': error_message,
            'error_type': 'System Error'
        })
    
    def log_message(self, format, *args):
        # Suppress default HTTP logging
        return

def start_server():
    port = 8002
    server_address = ('', port)
    
    try:
        httpd = HTTPServer(server_address, AgentHandler)
        print("🚀 Starting AI Research Assistant Web Server...")
        print(f"🌐 Web interface available at: http://localhost:{port}")
        print("📱 You can also access it from other devices on your network")
        print("=" * 60)
        print("💡 Tips:")
        print("   - Open http://localhost:8002 in your web browser")
        print("   - Submit a request through the web form")
        print("   - Press Enter in the text area to submit")
        print("   - Click example cards to use pre-made requests")
        print("=" * 60)
        
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user (Ctrl+C)")
        print("👋 Thanks for using the AI Research Assistant!")
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Error starting server: [Errno 48] Address already in use")
            print("🔧 Please check your configuration and try again")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()