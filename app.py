from flask import Flask, request, render_template
from sele import run_scraper

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if request.method == 'POST':
        stock = request.form.get('stock')
        try:
            result = run_scraper(stock)
        except Exception as e:
            result['error'] = str(e)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
