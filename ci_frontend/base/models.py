# Create your models here.
from __future__ import unicode_literals

from django.db import models
from django.forms import CharField


class Project(models.Model):
    """
    This is a dummy model and not used at all
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(max_length=200)
    tools = models.CharField(max_length=100)  # space-separated values
    pub_date = models.DateTimeField()
    img_name = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class CommonStock(models.Model):
    """
    Defines the column field of the DB where all the S&P 500 companies are listed. This DB will be used
    when the user searches for a particular company from the search option in Common Stock section
    eg
     - symbol = Ticker symbol of the company like 'aapl' for Apple Inc
     - Name = Is the full legal registered name with the SEC like "Apple Inc."
     - Sector = Industry type classification , like 'appl' = Apple Inc | Information Technology
    """
    # For the column names see the constutients_csv file which contains all the S&P 500 companies
    symbol = models.CharField(max_length=100,
                              default='None')
    Name = models.CharField(max_length=200,
                            default='None')
    Sector = models.CharField(max_length=100,
                              default='None')
    # This one is not part of the csv file but added to keep this search limited to Common stock
    # which depend on 10-k form reports
    form_type = models.CharField(max_length=25,
                                 default='10-k')
    class Meta:
        db_table = "commonstock"

    def __str__(self):
        return self.symbol
