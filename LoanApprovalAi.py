import json
import csv
from typing import Dict, List, Union, Tuple
from datetime import datetime
import io
import re

class LoanApprovalSystem:
    def __init__(self):
        self.required_fields = ['applicant_id', 'credit_score', 'annual_income', 'monthly_debt_payments']
        self.numeric_fields = ['credit_score', 'annual_income', 'monthly_debt_payments']


    def generate_validation_report(self, data: List[Dict]) -> str:
        """Generate a detailed validation report."""
        report = []
        report.append("# Data Validation Report\n")
        
        # 1. Data Structure Check
        report.append("## 1. Data Structure Check:\n")
        report.append(f"- Number of applications: {len(data)}\n")
        report.append(f"- Number of fields: {len(self.required_fields)}\n\n")
        
        # 2. Required Fields Check
        report.append("## 2. Required Fields Check:\n")
        for field in self.required_fields:
            present = all(field in record for record in data)
            report.append(f"- {field}: {'✓' if present else '✗'}\n")
        report.append("\n")
        
        # 3. Data Type Validation
        report.append("## 3. Data Type Validation:\n")
        validation_results = {
            'credit_score': {'name': 'Credit Score (positive number)', 'valid': True},
            'annual_income': {'name': 'Annual Income (positive number)', 'valid': True},
            'monthly_debt_payments': {'name': 'Monthly Debt Payments (non-negative number)', 'valid': True}
        }
        
        for record in data:
            for field in self.numeric_fields:
                try:
                    value = float(record[field])
                    if field == 'credit_score' and value <= 0:
                        validation_results[field]['valid'] = False
                    elif field == 'annual_income' and value <= 0:
                        validation_results[field]['valid'] = False
                    elif field == 'monthly_debt_payments' and value < 0:
                        validation_results[field]['valid'] = False
                except (ValueError, TypeError):
                    validation_results[field]['valid'] = False
        
        for field, result in validation_results.items():
            report.append(f"- {result['name']}: {'✓' if result['valid'] else '✗'}\n")
        
        # Validation Summary
        all_valid = all(result['valid'] for result in validation_results.values())
        report.append("\n## Validation Summary:\n")
        if all_valid:
            report.append("Data validation is successful! Proceeding with analysis...\n")
        else:
            report.append("Data validation failed. Please correct the errors and resubmit.\n")
        
        # Formulas Used
        report.append("\n# Formulas Used:\n")
        report.append("1. Monthly Income Formula:\n")
        report.append("   $\\text{Monthly Income} = \\frac{\\text{Annual Income}}{12}$\n\n")
        report.append("2. Debt-to-Income (DTI) Ratio Formula:\n")
        report.append("   $\\text{DTI} = \\frac{\\text{Monthly Debt Payments}}{\\text{Monthly Income}}$\n\n")
        
        return "".join(report)
        
    def check_language(self, text: str) -> bool:
        """Check if input contains non-English characters."""
        # Simple check for common non-English characters
        non_english_pattern = r'[^\x00-\x7F]+'
        return bool(re.search(non_english_pattern, text))

    def validate_format(self, data_str: str, format_type: str) -> Tuple[bool, str]:
        """Validate the format of input data."""
        if format_type.lower() not in ['json', 'csv']:
            return False, self.get_template_message()
        
        try:
            if format_type.lower() == 'json':
                data = json.loads(data_str)
                if 'applicants' not in data:
                    return False, "ERROR: Invalid JSON structure. Missing 'applicants' key."
            elif format_type.lower() == 'csv':
                csv_file = io.StringIO(data_str)
                reader = csv.DictReader(csv_file)
                headers = reader.fieldnames
                if not headers or not all(field in headers for field in self.required_fields):
                    return False, "ERROR: Invalid CSV structure. Missing required headers."
        except (json.JSONDecodeError, csv.Error):
            return False, self.get_template_message()
            
        return True, "Format validation successful"

    def get_template_message(self) -> str:
        """Return template message for invalid format."""
        return """ERROR: Invalid data format. Please provide data in CSV or JSON format.

Here's the template:

CSV Format Example:
```csv
applicant_id,credit_score,annual_income,monthly_debt_payments
x,x,x,x
x,x,x,x
```

JSON Format Example:
```json
{
  "applicants": [
    {
      "applicant_id": "x",
      "credit_score": x,
      "annual_income": x,
      "monthly_debt_payments": x
    }
  ]
}
```
Please provide your data in CSV or JSON format to begin the analysis."""

    def validate_data(self, data: List[Dict]) -> Tuple[bool, str]:
        """Validates the input data according to specified rules."""
        for record in data:
            # Check for missing fields
            missing_fields = [field for field in self.required_fields if field not in record]
            if missing_fields:
                return False, f"ERROR: Missing required field(s): {', '.join(missing_fields)}."
            
            # Check data types
            invalid_types = []
            for field in self.numeric_fields:
                try:
                    float(record[field])
                except (ValueError, TypeError):
                    invalid_types.append(field)
            if invalid_types:
                return False, f"ERROR: Invalid data type for field(s): {', '.join(invalid_types)}. Please ensure numeric values."
            
            # Check value constraints
            invalid_values = []
            if float(record['credit_score']) <= 0:
                invalid_values.append('credit_score')
            if float(record['annual_income']) <= 0:
                invalid_values.append('annual_income')
            if float(record['monthly_debt_payments']) < 0:
                invalid_values.append('monthly_debt_payments')
            
            if invalid_values:
                return False, f"ERROR: Invalid value for field(s): {', '.join(invalid_values)}. Please correct and resubmit."
            
            # Check for non-USD currency indicators
            currency_fields = ['annual_income', 'monthly_debt_payments']
            for field in currency_fields:
                if isinstance(record[field], str) and any(symbol in record[field] for symbol in ['€', '£', '¥']):
                    return False, "ERROR: Unsupported currency detected. Please use USD."
        
        return True, "Data validation successful"

    def calculate_dti(self, annual_income: float, monthly_debt_payments: float) -> float:
        """Calculate Debt-to-Income ratio."""
        monthly_income = annual_income / 12
        dti = monthly_debt_payments / monthly_income
        return round(dti, 2)

    def determine_eligibility(self, credit_score: float, annual_income: float, dti: float) -> Tuple[str, str]:
        """Determine loan eligibility status and provide explanation."""
        if credit_score >= 700 and annual_income >= 50000 and dti < 0.35:
            status = "Approved"
            explanation = f"Approved because credit score {credit_score} is above 700, annual income {annual_income} is above 50000, and DTI {dti} is below 0.35"
        elif credit_score < 600 or annual_income < 30000 or dti > 0.50:
            status = "Declined"
            explanation = f"Declined because {'credit score is below 600' if credit_score < 600 else 'annual income is below 30000' if annual_income < 30000 else 'DTI is above 0.50'}"
        else:
            status = "Further Review"
            explanation = "Application requires further review due to borderline values"
        
        return status, explanation

    def generate_report(self, applicants: List[Dict]) -> str:
        """Generate a detailed report for all applicants."""
        report = []
        
        # First add validation report
        report.append(self.generate_validation_report(applicants))
        
        # Loan Application Summary
        report.append("\n# Loan Application Summary\n")
        report.append(f"Total Applicants Evaluated: {len(applicants)}\n")
        
        # Detailed Analysis for each applicant
        report.append("\n# Detailed Analysis\n")
        for applicant in applicants:
            report.append(f"\n## Applicant {applicant['applicant_id']}\n")
            
            # Input Data
            report.append("### Input Data:\n")
            report.append(f"- Credit Score: {applicant['credit_score']}\n")
            report.append(f"- Annual Income: ${float(applicant['annual_income']):,.2f}\n")
            report.append(f"- Monthly Debt Payments: ${float(applicant['monthly_debt_payments']):,.2f}\n")
            
            # Calculations
            annual_income = float(applicant['annual_income'])
            monthly_debt = float(applicant['monthly_debt_payments'])
            monthly_income = annual_income / 12
            dti = self.calculate_dti(annual_income, monthly_debt)
            
            report.append("\n### Detailed Calculations:\n")
            report.append("Monthly Income Calculation:\n")
            report.append(f"$\\text{{Monthly Income}} = \\frac{{{annual_income:,.2f}}}{{12}} = {monthly_income:,.2f}$\n\n")
            report.append("DTI Calculation:\n")
            report.append(f"$\\text{{DTI}} = \\frac{{{monthly_debt:,.2f}}}{{{monthly_income:,.2f}}} = {dti}$\n")
            
            # Eligibility Status
            status, explanation = self.determine_eligibility(float(applicant['credit_score']), 
                                                          annual_income, 
                                                          dti)
            report.append(f"\n### Final Eligibility Status: {status}\n")
            report.append(f"Explanation: {explanation}\n")
            
            # Summary Stats
            report.append("\n### Application Summary:\n")
            report.append(f"- Credit Score: {applicant['credit_score']}\n")
            report.append(f"- Monthly Income: ${monthly_income:,.2f}\n")
            report.append(f"- DTI Ratio: {dti}\n")
            report.append(f"- Status: {status}\n")
        
        # Feedback Request
        report.append("\n# Feedback Request\n")
        report.append("Would you like detailed calculations for any specific applicant? Rate this analysis (1-5).")
        
        return "".join(report)

    def handle_feedback(self, rating: int) -> str:
        """Handle user feedback based on rating."""
        if rating >= 4:
            return "Thank you for your positive feedback!"
        else:
            return "How can we improve our loan evaluation process?"

    def process_input(self, data_str: str, format_type: str) -> str:
        """Process input data and generate report."""
        # Check for non-English characters
        if self.check_language(data_str):
            return "ERROR: Unsupported language detected. Please use ENGLISH."
        
        # Validate format
        is_valid_format, format_message = self.validate_format(data_str, format_type)
        if not is_valid_format:
            return format_message
        
        try:
            if format_type.lower() == 'json':
                data = json.loads(data_str)
                applicants = data['applicants']
            elif format_type.lower() == 'csv':
                csv_file = io.StringIO(data_str)
                reader = csv.DictReader(csv_file)
                applicants = list(reader)
            
            # Validate data
            is_valid, message = self.validate_data(applicants)
            if not is_valid:
                return message
            
            # Generate report
            return self.generate_report(applicants)
            
        except Exception as e:
            return f"ERROR: An unexpected error occurred: {str(e)}"

# Example usage
def main():
    # Example data in both formats
    json_data = '''
    {
  "applicants": [
    {
      "applicant_id": "A001",
      "credit_score": 720,
      "annual_income": 60000,
      "monthly_debt_payments": 800
    },
    {
      "applicant_id": "A002",
      "credit_score": 580,
      "annual_income": 28000,
      "monthly_debt_payments": 500
    },
    {
      "applicant_id": "A003",
      "credit_score": 700,
      "annual_income": 52000,
      "monthly_debt_payments": 800
    },
    {
      "applicant_id": "A004",
      "credit_score": 680,
      "annual_income": 45000,
      "monthly_debt_payments": 700
    },
    {
      "applicant_id": "A005",
      "credit_score": 750,
      "annual_income": 90000,
      "monthly_debt_payments": 1500
    }
  ]
}
'''
    
    csv_data = ''''''

    loan_system = LoanApprovalSystem()
    
    
    # Process valid data
    print("\nProcessing JSON data:")
    print(loan_system.process_input(json_data, 'json'))
    
    print("\nProcessing CSV data:")
    print(loan_system.process_input(csv_data, 'csv'))
    
    # Example feedback handling
    print("\nHandling feedback:")
    print(loan_system.handle_feedback(5))
    print(loan_system.handle_feedback(2))

if __name__ == "__main__":
    main()