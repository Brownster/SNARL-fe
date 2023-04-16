from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import base64
from io import BytesIO


def Heat_count_alerts_per_node_hour(file_path, start_date=None, end_date=None):
    # Read in the alert data from a CSV file
    df = pd.read_csv(file_path)

    # Convert the 'Initial event generation time' column to datetime
    df['Initial event generation time'] = pd.to_datetime(df['Initial event generation time'])

    # Filter the data by date range, if provided
    if start_date and end_date:
        mask = (df['Initial event generation time'] >= start_date) & (df['Initial event generation time'] <= end_date)
        df = df.loc[mask]

    # Extract the hour of the day from the 'Initial event generation time' column
    df['Hour of Day'] = df['Initial event generation time'].dt.hour

    # Group the data by node and hour of the day, then count the number of alerts
    count_per_node_hour = df.groupby(['Node', 'Hour of Day'])['Number'].count().unstack()

    # Fill NaN values with 0
    count_per_node_hour = count_per_node_hour.fillna(0).astype(int)

    # Plot a heatmap of the results
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(count_per_node_hour, annot=True, fmt='d', ax=ax)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Node")
    ax.set_title("Number of Alerts per Node per Hour of Day")

    # Save the figure as a PNG image
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    heatmap_img = base64.b64encode(buffer.getvalue()).decode()

    plt.close(fig)

    return heatmap_img





def count_top_additional_information(file_path, start_date=None, end_date=None):
    # Read in the alert data from a CSV file
    df = pd.read_csv(file_path)

    # Convert the 'Initial event generation time' column to datetime
    df['Initial event generation time'] = pd.to_datetime(df['Initial event generation time'])

    # Filter the data by date range, if provided
    if start_date and end_date:
        mask = (df['Initial event generation time'] >= start_date) & (df['Initial event generation time'] <= end_date)
        df = df.loc[mask]

    # Group the data by 'Additional information' and count the number of alerts
    count_per_additional_info = df.groupby('Additional information')['Number'].count()

    # Sort the counts in descending order and get the top 10
    top_10_additional_info = count_per_additional_info.sort_values(ascending=False).head(10)

    # Create a list of dictionaries to store the results
    table_data = [{"additional_info": info, "count": count} for info, count in top_10_additional_info.items()]

    return table_data




def plot_alerts_per_node_day(file_path, start_date=None, end_date=None):
    # Read in the alert data from a CSV file
    df = pd.read_csv(file_path)

    # Convert the 'Initial event generation time' column to datetime
    df['Initial event generation time'] = pd.to_datetime(df['Initial event generation time'])

    # Filter the data by date range, if provided
    if start_date and end_date:
        mask = (df['Initial event generation time'] >= start_date) & (df['Initial event generation time'] <= end_date)
        df = df.loc[mask]

    # Extract the day of the week from the 'Initial event generation time' column
    df['Day of Week'] = df['Initial event generation time'].dt.day_name()

    # Group the data by node and day of the week, then count the number of alerts
    count_per_node_day = df.groupby(['Node', 'Day of Week'])['Number'].count().unstack()

    # Fill NaN values with 0
    count_per_node_day = count_per_node_day.fillna(0).astype(int)

    # Create a bar plot using matplotlib
    ax = count_per_node_day.plot(kind='bar', stacked=True, figsize=(10, 5))
    ax.set_ylabel('Number of Alerts')
    ax.set_title('Alerts per Node by Day of Week')

    # Save the plot to a bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode()

    # Close the plot to avoid memory leak
    plt.close()

    return img_data


def count_alerts_per_node_day(file_path, start_date=None, end_date=None):
    # Read in the alert data from a CSV file
    df = pd.read_csv(file_path)

    # Convert the 'Initial event generation time' column to datetime
    df['Initial event generation time'] = pd.to_datetime(df['Initial event generation time'])

    # Filter the data by date range, if provided
    if start_date and end_date:
        mask = (df['Initial event generation time'] >= start_date) & (df['Initial event generation time'] <= end_date)
        df = df.loc[mask]

    # Extract the day of the week from the 'Initial event generation time' column
    df['Day of Week'] = df['Initial event generation time'].dt.day_name()

    # Group the data by node and day of the week, then count the number of alerts
    count_per_node_day = df.groupby(['Node', 'Day of Week'])['Number'].count().unstack()

    # Fill NaN values with 0
    count_per_node_day = count_per_node_day.fillna(0).astype(int)

    # Convert the results to an HTML table using Pandas
    result_html = count_per_node_day.to_html()

    return result_html


###### counts per cust
def count_alerts_per_node(file_path, start_date=None, end_date=None):
    # Read in the alert data from a CSV file
    df = pd.read_csv(file_path)

    # Filter the data by date range, if provided
    if start_date and end_date:
        mask = (df['Initial event generation time'] >= start_date) & (df['Initial event generation time'] <= end_date)
        df = df.loc[mask]

    # Group the data by node and count the number of alerts for each node
    count_per_node = df.groupby('Node')['Number'].count()

    # Display the results in a table using PrettyTable
    table = PrettyTable()
    table.field_names = ["Node", "Number of Alerts"]
    for node, count in count_per_node.items():
        table.add_row([node, count])
    print(table)




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

@app.route('/heatmap', methods=['POST'])
def heatmap():
    file_path = request.form['file_path']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    heatmap_img = Heat_count_alerts_per_node_hour(file_path, start_date, end_date)

    return render_template('heatmap.html', heatmap_img=heatmap_img)


@app.route('/top_10_additional_info', methods=['POST'])
def top_10_additional_info():
    file_path = request.form['file_path']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    table_data = count_top_additional_information(file_path, start_date, end_date)

    return render_template('top_10_additional_info.html', table_data=table_data)


@app.route('/plot_alerts_per_node_day', methods=['POST'])
def plot_alerts_per_node_day_route():
    file_path = request.form['file_path']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    img_data = plot_alerts_per_node_day(file_path, start_date, end_date)
    return render_template('plot_alerts_per_node_day.html', img_data=img_data)


@app.route('/run_query', methods=['POST'])
def run_query():
    # ...
    elif query == 'Alerts by Node and Day':
        result = count_alerts_per_node_day(file_path, start_date, end_date)
    # ...
    return render_template('result.html', result=result)



if __name__ == '__main__':
    app.run(debug=True, port=8010)
