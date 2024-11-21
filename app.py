import os
from flask import Flask, render_template, request, jsonify, make_response
import pandas as pd
import io
import json

app = Flask(__name__)

# Define the master file path
# MASTER_FOLDER = "master"
MASTER_FOLDER = os.path.join(os.path.dirname(__file__), "master")

MASTER_FILE = "master.csv"

# Load cities.json file
with open("citynames.json", "r") as f:
    cities_data = json.load(f)

# Predefined lists of unique countries and cities
unique_countries = ['AMERICAN SAMOA', 'ANGOLA', 'ANGUILLA', 'Albania', 'Algeria', 'Andorra', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'BHUTAN', 'BRUNEI', 'BURKINA FASO', 'BURUNDI', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'British Virgin Islands', 'Bulgaria', 'CAPE VERDE', 'CHAD', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'COMOROS', 'CYPRUS', 'Cambodia', 'Cameroon', 'Canada', 'Caribbean Netherlands', 'Cayman Islands', 'Chile', 'China', 'Colombia', 'Congo - Brazzaville', 'Congo - Kinshasa', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'CuraÃ§ao', 'Czechia', 'DJIBOUTI', 'DOMINICA', 'Denmark', 'Dominican Republic', 'EQUATORIAL GUINEA', 'ERITREA', 'Ecuador', 'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'FAROE ISLANDS', 'FRENCH GUIANA', 'Fiji', 'Finland', 'France', 'French Polynesia', 'GUINEA-BISSAU', 'GUYANA', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 'Haiti', 'Honduras', 'Hong Kong', 'Hong Kong SAR China', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'KIRIBATI', 'Kazakhstan', 'Kenya', 'Kuwait', 'Kyrgyzstan', 'LESOTHO', 'LIBERIA', 'Laos', 'Latvia', 'Lebanon', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'MADAGASCAR', 'MAURITANIA', 'MAYOTTE', 'MONTSERRAT', 'Macau', 'Macau SAR China', 'Macedonia', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Martinique', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar (Burma)', 'NIGER', 'NIUE', 'Namibia', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Nigeria', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestinian Territories', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'RÃ©union', 'SAINT HELENA', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SIERRA LEONE', 'SOLOMON ISLANDS', 'SUDAN', 'SVALBARD AND JAN MAYEN', 'Saint BarthÃ©lemy', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin', 'Saint Vincent and Grenadines', 'Samoa', 'Saudi Arabia', 'Select', 'Senegal', 'Serbia', 'Seychelles', 'Singapore', 'Sint Maarten', 'Slovakia', 'Slovenia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'TRINIDAD AND TOBAGO', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States Of America', 'United States Virgin Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Wallis and Futuna', 'Zambia', 'Zimbabwe']


@app.route('/')
def index():
    # Check if the folder exists and the file is present
    file_path = os.path.join(MASTER_FOLDER, MASTER_FILE)
    if os.path.exists(file_path):
        file_status = {
            "exists": True,
            "file_name": MASTER_FILE
        }
    else:
        file_status = {
            "exists": False,
            "file_name": None
        }

    return render_template('index.html', file_status=file_status, countries=unique_countries)


@app.route('/process', methods=['POST'])
def process():
    try:
        # Load the master file
        file_path = os.path.join(MASTER_FOLDER, MASTER_FILE)
        data = pd.read_csv(file_path)

        # Define the mandatory columns
        mandatory_headers = [
            "Hotelid", "Hotelname", "Address", "Rating",
            "City", "Country", "CityId", "CountryId",
            "Latitude", "Longitude"
        ]

        # Get filters from the form
        country_filters = request.form.getlist('country_filter')
        city_filters = request.form.getlist('city_filter')
        rating_filters = request.form.getlist('rating_filter')  # New Ratings filter
        include_oth = request.form.get('is_oth_filter') == 'on'
        include_top_selling = request.form.get('top_selling_filter') == 'on'
        include_on_top_oth = request.form.get('on_top_oth_filter') == 'on'
        include_on_top_top_selling = request.form.get('on_top_top_selling_filter') == 'on'

        # Start with filtered data based on country, city, and ratings
        filtered_data = data.copy()

        # Apply country and city filters
        if country_filters or city_filters:
            filtered_data = filtered_data[
                (filtered_data['Country'].isin(country_filters)) |
                (filtered_data['City'].isin(city_filters))
            ]

        # Apply the new Ratings filter
        if rating_filters:
            rating_filters = [int(r) for r in rating_filters]  # Convert to integers
            filtered_data = filtered_data[filtered_data['Rating'].isin(rating_filters)]

        # Apply the original isOTH filter for selected countries/cities
        if include_oth:
            filtered_data = filtered_data[filtered_data['isOTH'] == 1]

        # Apply the original TopSelling filter for selected countries/cities
        if include_top_selling:
            filtered_data = filtered_data[filtered_data['TopSoldHotel'] == 1]

        # Prepare "On Top" data
        on_top_data = pd.DataFrame()
        if include_on_top_oth:
            # Add all isOTH=1 records from the master file
            on_top_oth_data = data[data['isOTH'] == 1]
            on_top_data = pd.concat([on_top_data, on_top_oth_data])

        if include_on_top_top_selling:
            # Add all TopSelling=1 records from the master file
            on_top_top_selling_data = data[data['TopSoldHotel'] == 1]
            on_top_data = pd.concat([on_top_data, on_top_top_selling_data])

        # Combine filtered data with "On Top" data
        combined_data = pd.concat([filtered_data, on_top_data]).drop_duplicates(subset=["Hotelid"])

        # Select the mandatory columns
        selected_columns = mandatory_headers.copy()

        # Add optional columns based on user selection
        if request.form.get('include_ean'):
            selected_columns.append('EAN')

        if request.form.get('include_agoda'):
            selected_columns.append('AGODA')

        if request.form.get('include_ean_agoda'):
            selected_columns.extend(['EAN', 'AGODA'])

        if request.form.get('include_travelgate'):
            selected_columns.append('Travelgate')

        if request.form.get('include_unicaid'):
            selected_columns.append('Unicaid')

        # Filter the final data with selected columns
        final_data = combined_data[selected_columns]

        # Prepare the CSV output
        buffer = io.StringIO()
        final_data.to_csv(buffer, index=False)

        output = make_response(buffer.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=filtered_data.csv"
        output.headers["Content-type"] = "text/csv"

        return output

    except Exception as e:
        return jsonify({"error": f"Error during processing: {str(e)}"}), 500

    
@app.route('/get_cities_by_letter', methods=['POST'])
def get_cities_by_letter():
    data = request.get_json()
    search_term = data.get('search_term', '').capitalize()

    if not search_term:
        return jsonify({"cities": []})

    first_letter = search_term[0].upper()
    matching_cities = [
        city for city in cities_data.get(first_letter, [])
        if city.lower().startswith(search_term.lower())
    ]
    return jsonify({"cities": matching_cities})


if __name__ == "__main__":
    app.run(debug=False)
