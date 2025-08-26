from flask import Flask, render_template, request, redirect, url_for, flash
from finance_advisor import FinanceAdvisor


def create_app() -> Flask:
	"""Factory to create and configure the Flask application.

	This keeps the app creation explicit and testable.
	"""
	app = Flask(__name__)
	# In a real app, keep the secret key secret. Used for flashing messages.
	app.config["SECRET_KEY"] = "dev-secret-key-change-me"

	@app.route("/", methods=["GET"]) 
	def index():
		"""Render the homepage with the financial goal form."""
		return render_template("index.html")

	@app.route("/results", methods=["POST"]) 
	def results():
		"""Handle form submission, validate input, and render the results page.

		Basic validation ensures required fields are present. If any field is blank,
		an error message is shown and the user is redirected back to the form.
		"""
		# Retrieve form data safely using .get to avoid KeyErrors
		financial_goal = request.form.get("financial_goal", "").strip()
		timeframe = request.form.get("timeframe", "").strip()
		current_savings = request.form.get("current_savings", "").strip()
		monthly_income = request.form.get("monthly_income", "").strip()
		monthly_expenses = request.form.get("monthly_expenses", "").strip()
		risk_tolerance = request.form.get("risk_tolerance", "").strip()

		# Collect missing fields for helpful error feedback
		missing = []
		if not financial_goal:
			missing.append("What is your financial goal?")
		if not timeframe:
			missing.append("What is your target timeframe to achieve this goal?")
		if not current_savings:
			missing.append("What is your current savings?")
		if not monthly_income:
			missing.append("What is your monthly income?")
		if not monthly_expenses:
			missing.append("What are your monthly expenses?")
		if not risk_tolerance:
			missing.append("What is your risk tolerance?")

		if missing:
			# Flash a combined error message and send the user back to the form
			flash("Please complete all fields before submitting.")
			for field in missing:
				flash(f"Missing: {field}")
			return redirect(url_for("index"))

		# Create user data dictionary for the finance advisor
		user_data = {
			"financial_goal": financial_goal,
			"timeframe": timeframe,
			"current_savings": current_savings,
			"monthly_income": monthly_income,
			"monthly_expenses": monthly_expenses,
			"risk_tolerance": risk_tolerance,
		}

		try:
			# Initialize finance advisor and generate advice
			advisor = FinanceAdvisor()
			advice_list = advisor.generate_financial_advice(user_data)
		except Exception as e:
			# If finance advisor fails, provide fallback advice
			flash(f"AI analysis temporarily unavailable: {str(e)}")
			flash("Showing general financial advice instead.")
			advice_list = [
				{
					"recommendation": "Build Emergency Fund",
					"explanation": "Start by saving 3-6 months of expenses in a high-yield savings account.",
					"growth_projection": f"With consistent monthly contributions, you could build a substantial emergency fund over {timeframe} years.",
					"risks": "Low risk, but inflation may reduce purchasing power over time."
				},
				{
					"recommendation": "Diversified Investment Portfolio",
					"explanation": f"Based on your {risk_tolerance} risk tolerance, consider a mix of stocks, bonds, and other assets.",
					"growth_projection": f"Historical market returns suggest potential growth of 6-8% annually over {timeframe} years.",
					"risks": "Market volatility and potential for loss of principal."
				}
			]

		# Render results with advice
		return render_template(
			"results.html",
			financial_goal=financial_goal,
			timeframe=timeframe,
			current_savings=current_savings,
			monthly_income=monthly_income,
			monthly_expenses=monthly_expenses,
			risk_tolerance=risk_tolerance,
			advice_list=advice_list,
		)

	return app


if __name__ == "__main__":
	# Allow running via `python app.py` for local development
	app = create_app()
	# Debug mode provides auto-reload and better error pages during development
	app.run(host="0.0.0.0", port=8000, debug=True)

