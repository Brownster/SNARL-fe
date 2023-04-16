from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Import the functions from your existing code
from alert_functions import count_alerts_per_node, count_alerts_per_node_day, plot_alerts_per_node_day, count_top_additional_information, Heat_count_alerts_per_node_hour

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')

        # Check if a file is uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type')
            return redirect(request.url)

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        start_date = request.form.get('start_date') or None
        end_date = request.form.get('end_date') or None

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Call the appropriate function based on the selected query
        try:
            if query == 'Number of Alerts by Node':
                result = count_alerts_per_node(file_path, start_date, end_date)
            elif query == 'Alerts by Node and Day':
                result = count_alerts_per_node_day(file_path, start_date, end_date)
            elif query == 'Plot Alerts by Node and Day':
                result = plot_alerts_per_node_day(file_path, start_date, end_date)
            elif query == 'Top 10 Additional Information':
                result = count_top_additional_information(file_path, start_date, end_date)
            elif query == 'Heat Map of Alerts By Customer By Hour':
                result = Heat_count_alerts_per_node_hour(file_path, start_date, end_date)
            else:
                flash('Invalid query selected')
                return redirect(request.url)

            # Handle the result of the function call (display, save as file, etc.)
            # You may need to modify the functions to return the results instead of printing them directly

        except FileNotFoundError:
            flash('File not found')
        except Exception as e:
            flash(str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8010)
