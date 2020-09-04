from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.


def index(request):
    buf = ["""<div>


            <div id="2d56a5a7-a7d0-4e9b-a195-de6cab2be27d" class="plotly-graph-div" style="height:100%; width:100%;"></div>
            <script type="text/javascript">

                    window.PLOTLYENV=window.PLOTLYENV || {};
                    window.PLOTLYENV.BASE_URL='https://plot.ly';

                if (document.getElementById("2d56a5a7-a7d0-4e9b-a195-de6cab2be27d")) {
                    Plotly.newPlot(
                        '2d56a5a7-a7d0-4e9b-a195-de6cab2be27d',
                        [{"line": {"color": "deepskyblue"}, "name": "Assets", "type": "scatter", "uid": "b9467a96-c331-463c-a582-085260ee3ef9", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [286556.0, 258848.0, 241086.0, 193694.0, 176223.0]}, {"line": {"color": "dimgray"}, "name": "Cash and Cash Equ", "type": "scatter", "uid": "26d9c147-ffd1-48f9-b55c-955cc026bec1", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [11356.0, 11946.0, 7663.0, 6510.0, 5595.0]}, {"line": {"color": "pink"}, "name": "Other Assets", "type": "scatter", "uid": "70d50f18-143d-452c-9bd2-2c8a7c342fec", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [10146.0, 6751.0, 4897.0, 5892.0, 5461.0]}, {"line": {"color": "green"}, "name": "Long term investments", "type": "scatter", "uid": "bc069a1c-a689-4755-bf62-5599bd5c3663", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [2649.0, 1862.0, 6023.0, 10431.0, 12053.0]}, {"line": {"color": "purple"}, "name": "Property and other equipment", "type": "scatter", "uid": "6929577e-61bf-4ceb-8170-3f8640f69b83", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [36477.0, 29460.0, 23734.0, 18356.0, 14731.0]}],
                        {"title": {"text": "Time Series with Assets, Cash, Other Assets, LTA, Property"}, "xaxis": {"rangeslider": {"visible": true}}},
                        {"showLink": false, "linkText": "Export to plot.ly", "responsive": true, "plotlyServerURL": "https://plot.ly"}
                    )
                };

            </script>
        </div> """,
           """
            <div>


            <div id="b3ef125d-8881-4217-b0ee-ec162591fcd3" class="plotly-graph-div" style="height:100%; width:100%;"></div>
            <script type="text/javascript">

                    window.PLOTLYENV=window.PLOTLYENV || {};
                    window.PLOTLYENV.BASE_URL='https://plot.ly';

                if (document.getElementById("b3ef125d-8881-4217-b0ee-ec162591fcd3")) {
                    Plotly.newPlot(
                        'b3ef125d-8881-4217-b0ee-ec162591fcd3',
                        [{"line": {"color": "deepskyblue"}, "name": "Liabilities", "type": "scatter", "uid": "20ad29c2-6f8a-49e3-bacb-886b8495a743", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [184226.0, 176130.0, 168692.0, 121697.0, 96140.0]}, {"line": {"color": "dimgray"}, "name": "Goodwill", "type": "scatter", "uid": "9304561b-4ee7-4384-bfae-0b596cb46ed2", "x": ["2019", "2018", "2017", "2016", "2015"], "y": [42026.0, 35683.0, 35122.0, 17872.0, 16939.0]}],
                        {"title": {"text": "Time Series with Liabilities and Goodwill"}, "xaxis": {"rangeslider": {"visible": true}}},
                        {"showLink": false, "linkText": "Export to plot.ly", "responsive": true, "plotlyServerURL": "https://plot.ly"}
                    )
                };

            </script>
        </div>
           """]
    context = {
        'output': buf
    }
    return render(request, 'base/home.html', context)
