from django import forms


class WeatherForm(forms.Form):
    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        initial=51.231,
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        initial=-2.3218,
    )
