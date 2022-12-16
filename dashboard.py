# Import libraries
import streamlit as st
import pandas as pd
import requests
import statistics as sts
import plotly.express as px

# Reduce margins of layout
st.set_page_config(layout = "wide")

# Hiding arrow from metric
st.write(
	"""
	<style>
	[data-testid="stMetricDelta"] svg {
		display: none;
	}
	</style>
	""",
	unsafe_allow_html=True)

# Insert title
st.title("Physical Risk Prediction of your Portfolio")

# Upload the file
uploaded_file = st.file_uploader("Upload your portfolio", type = ["csv"])

# If the file exists
if uploaded_file is not None:
	# Import the dataframe
	portfolio = pd.read_csv(uploaded_file)

	# Rename columns
	portfolio = portfolio.rename(columns = {
		"Carbon Intensity - Scope 1 (tonnes CO2e/USD mn)": "Scope 1",
		"Carbon Intensity - Scope 2 (tonnes CO2e/USD mn)": "Scope 2",
		"Carbon Intensity - Scope 3 (tonnes CO2e/USD mn)": "Scope 3"})

	# Call the API endpoint created on Wolfram Cloud
	endpoint = "https://www.wolframcloud.com/obj/dario.scalabrin/WebServices/APIRiskRating"

	# Create an empty list where to store predictions
	pred_ratings = []

	# Progress bar initialisation
	my_bar = st.progress(0)
	
	# Going through each asset of the portfolio
	for i in range(len(portfolio)):
		line = portfolio.iloc[i]

		# Create a dictionary with the requested values
		request_body = {
			"Sector" : line["Sector"],
			"CarbInt1" : line["Scope 1"],
			"CarbInt2" : line["Scope 2"],
			"CarbInt3" : line["Scope 3"],
			"Country" : line["Country"].upper(),
			"CarbDisc" : line["Carbon Disclosure"],
			"Revenues" : line["Revenue (USD mn)"]
			}
		
		# Do a API post call
		response = requests.post(endpoint, data = request_body)
		
		# Extract the value predicted
		t = response.text.replace('"', '')
		
		# Append to the empty list
		pred_ratings.append(t)

		# Percentage completed
		perc_completed = i/len(portfolio)

		# Display the progress bar
		my_bar.progress(perc_completed+(1/len(portfolio)))
		
	# Show animation when all predictions are done    
	st.balloons()
	
	# Add the ratings to the porfolio
	portfolio["Ratings"] = pred_ratings
	
	# Sort them in ascending way
	portfolio = portfolio.sort_values(by = ['Ratings'])

	# Convert the ratings in numerical values
	def conversion_rat_score(rating):
		converted_list = []
		for i in rating:
			if i == "A":
				converted_list.append(0.1)
			elif i == "B":
				converted_list.append(0.3)
			elif i == "C":
				converted_list.append(0.5)
			elif i == "D":
				converted_list.append(0.7)
			elif i == "E":
				converted_list.append(0.9)
		return converted_list
	
	# Convert numerical values in ratings
	def conversion_score_rat(score):
		if 0.0 <= score <= 0.2:
			return ("A")
		elif 0.2 <= score <= 0.4:
			return ("B")
		elif 0.4 <= score <= 0.6:
			return ("C")
		elif 0.6 <= score <= 0.8:
			return ("D")
		elif 0.8 <= score <= 1.0:
			return ("E")

	# Convert rating in numerical values
	pf_rat_numbers = conversion_rat_score(portfolio["Ratings"])
	
	# Add them to the portfolio
	portfolio["Ratings_value"] = pf_rat_numbers
	
	# Compute the average rating for the portfolio
	pf_score_avg = conversion_score_rat(sum([a * b for a,b in zip(portfolio["Percentage"], portfolio["Ratings_value"])])/100)

	# Create color palette for rating display
	palette = ["#8CD47E", "#7ABD7E", "#F8D66D", "#FFB54C","#FF6961"]
	ratings_in_pf = sorted(list(set(portfolio["Ratings"])))
	all_ratings = ["A", "B", "C", "D", "E"]

	# Adapt the palette to prediction present in dataset
	new_palette = []
	for i in range(len(all_ratings)):
		if ratings_in_pf.count(all_ratings[i]) == 1:
			new_palette.append(palette[i])

	# Qualitative translation of risk ratings 
	if pf_score_avg == "A":
		delta = "Low Risk"
	elif pf_score_avg == "B":
		delta = "Low-Medium Risk"
	elif pf_score_avg == "C":
		delta = "Medium Risk"
	elif pf_score_avg == "D":
		delta = "Medium-High Risk"
	elif pf_score_avg == "E":
		delta = "High Risk"

	# Show portfolio rating 
	st.metric(label = "Weighted Portfolio Rating",  value = pf_score_avg, delta = delta, delta_color = "off")
	
	# Create 2x2 display: the first row gives title and short explanation, the second row displays the graph
	col1_A, col2_A, = st.columns(2)
	with col1_A:
		# Insert title
		st.markdown("#### Distribution of Physical Risk Ratings")
		st.markdown("The following graph shows the distribution of predicted physical risk ratings of all the companies in the portfolio.")
		
	with col2_A:
		# Insert title
		st.markdown("#### Summary statistics of Physical Risk Ratings")
		st.markdown("The following graph shows summary statistics of the predicted ratings of the given portfolio: median, minimum, maximum and quartiles. The graph also displays the sectors of each company, by hovering above each data point")
		
	col1_B, col2_B, = st.columns(2)
	with col1_B:
		# Insert graph
		fig_histogram = px.histogram(portfolio, x = "Ratings",
					   y = "Percentage",
					   color = "Ratings",
					   color_discrete_map = {ratings_in_pf[i]: new_palette[i] for i in range(len(ratings_in_pf))})
		st.plotly_chart(fig_histogram, use_container_width = True)

	with col2_B:
		# Insert graph
		fig_violin = px.violin(portfolio, y="Ratings", box=True, hover_name = "Sector", points='all')
		fig_violin.update_yaxes(autorange="reversed", type='category')
		st.plotly_chart(fig_violin, use_container_width = True)

	# Create 2x2 display: the first row gives title and short explanation, the second row displays the graph
	col3_A, col4_A, = st.columns(2)
	with col3_A:
		# Insert title
		st.markdown("#### Sectorial split of Physical Risk Ratings")
		st.markdown("The following graph shows how the predicted ratings are distributed across each sector. For each sector, a company is weighted to the corresponding invested percentage in the portfolio.")

	with col4_A:
		# Insert title
		st.markdown("#### Ternary Plot of Carbon Intensity Scopes")
		st.markdown("The following graph shows Carbon Intensity across the 3 scopes. The size of each bubble corresponds to the invested percentage of a company in the portfolio. For each company, the graph also displays additional information, i.e. Sector, Quantified Carbon Intensities, Portfolio Weights and its rating, by hovering above each data point.")

	col3_B, col4_B, = st.columns(2)
	with col3_B:
		# Insert graph
		fig_sectors = px.histogram(portfolio, x = "Sector",
				   y = "Percentage", color = "Ratings",
				   barnorm = 'percent', text_auto='.0f',
				   title="",
				   color_discrete_map = {ratings_in_pf[i]: new_palette[i] for i in range(len(ratings_in_pf))})
		st.plotly_chart(fig_sectors, use_container_width = True)

	with col4_B:
		# Insert graph
		fig_triangle = px.scatter_ternary(portfolio,
						 a = "Scope 1",
						 b = "Scope 2",
						 c = "Scope 3",
						 hover_name = "Sector",
						 color = "Ratings",
						 size = "Percentage",
						 size_max = 15,
						 color_discrete_sequence = new_palette)
		st.plotly_chart(fig_triangle, use_container_width = True)

# Insert banner with proposed default portfolio
else:
	st.info(
		f"""
			👆 Upload a .csv file first. Sample to try: [portfolio.csv](https://drive.google.com/uc?export=download&id=1-KTlI3biZg5-UpU2pwXicLlu_I3k-1nv)
			"""
	)
# Stop the script
	st.stop()	