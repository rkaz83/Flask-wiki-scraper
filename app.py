from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import pandas as pd
import requests

app = Flask(__name__)

# Store tables globally (not recommended for production but okay for small app)
SCRAPED_TABLES = []


@app.route('/', methods=['GET', 'POST'])
def home():
    global SCRAPED_TABLES
    SCRAPED_TABLES = []
    tables_found = 0
    df_html = None
    selected_table = None

    if request.method == 'POST':
        url = request.form.get('url')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/142.0.0.0 Safari/537.36"
        }

        try:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'lxml')

            # Find ALL tables
            tables = soup.find_all('table')

            if not tables:
                return "No tables found on this webpage."

            # Convert all tables to DataFrames
            SCRAPED_TABLES = [pd.read_html(str(t))[0] for t in tables]
            tables_found = len(SCRAPED_TABLES)

            return render_template("index.html",
                                   tables_found=tables_found,
                                   table=None,
                                   selected=None)

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html", tables_found=0, table=None, selected=None)


@app.route('/table/<int:index>')
def show_table(index):
    global SCRAPED_TABLES

    try:
        df = SCRAPED_TABLES[index]
        df_html = df.to_html(classes='table table-bordered', index=False)

        return render_template("index.html",
                               tables_found=len(SCRAPED_TABLES),
                               table=df_html,
                               selected=index)
    except:
        return "Invalid table index."


@app.route('/download/csv/<int:index>')
def download_csv(index):
    df = SCRAPED_TABLES[index]
    filename = f"table_{index}.csv"
    df.to_csv(filename, index=False)
    return send_file(filename, as_attachment=True)


@app.route('/download/excel/<int:index>')
def download_excel(index):
    df = SCRAPED_TABLES[index]
    filename = f"table_{index}.xlsx"
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
