#  Predicting Climate Risks :zap:

This project aims at predicting the Physical Risk Rating of a portfolio.<br>
You can access our interactive dashboard at [this link](https://pred-climate-risks.streamlit.app) and try it yourself!:nerd_face:

## Introduction :information_desk_person:
The summer of 2022 was the hottest in Europe's recorded history. The frequency of extreme events is rapidly increasing, which means that **Climate Risk is becoming more and more a Business Risk**. For this reason, there is an emerging interests from investors to understand the physical risk of the assets of the companies that they want to invest in. 

## Data :bar_chart:
For this project, we used [Trucost](https://www.marketplace.spglobal.com/en/datasets) datasets, in particular we used [Environmental Information](https://www.marketplace.spglobal.com/en/datasets/trucost-environmental-(46)) of each company and [asset level physical risk](https://www.marketplace.spglobal.com/en/datasets/physical-risk-(148)) dataset. The latter includes information on physical risk exposures of company assets to extreme events (i.e., Water Stress, Flood, Heatwave, Coldwave, Hurricane, Wildfire, Sea Level Rise, Coastal Flood). The exposures are calculated using climate change scenarios based on IPCC Representative Concentration Pathways (RCP), namely:
- **Low Climate Change Scenario (RCP 2.6)**: Aggressive mitigation actions to halve emissions by 2050. This scenario is likely to result in warming of less than 2 degree Celsius by 2100.
- **Moderate Climate Change Scenario (RCP 4.5)**: Strong mitigation actions to reduce emissions to half of current levels by 2080. This scenario is more likely than not to result in warming in excess of 2 degrees Celsius by 2100.
- **High Climate Change Scenario (RCP 8.5)**: Continuation of business as usual emissions growth. This scenario is expected to result in warming in excess of 4 degrees Celsius by 2100.

Trucost also provides "intermediate" scenarios, and for each of them the exposure score for each extreme event for the period 2020-2090. We decided to select Moderate-High scenario, because with the current policies it is the most likely to happen. 

## Development :wrench:
Our final model takes as a input:
- Sector
- Country
- Carbon-Intensity: Scope 1
- Carbon-Intensity: Scope 2
- Carbon-Intensity: Scope 3
- Carbon Disclosure
- Revenues

The model ouptut of the Physical Risk of one company, which can span from A to E, with A meaning low risk, and E high risk.

In order to do so, for each asset of each company, we took the Composite Physical Risk Score (i.e., an equal weighted additive combination of the company physical risk score on each indicator for a given scenario and year) and we computed the integral score as follows:

Let $f:$ $\mathbb{R} \to \mathbb{R} $, be the linear regression of the composite score $C_t$ for $t \in \{2020, \dots 2090\}$

$$  I = \int_{2020}^{2100} f(t) dt.  $$

Then, for each company we did the average of the integral scores of all its assets, and we rescaled the values using the Min-Max Method to obtain them in an interval between 0 and 1. Next, we converted each score in ratings, ranging from A to E. Below you can observe the distribution of what we obtained:

<p align="center"><img src="https://i.ibb.co/52r6pT8/Whats-App-Image-2022-12-11-at-18-25-55.jpg" width="400"/></p>

## Prediction :telescope:
Before choosing a particular prediction model, we tested several. In the table below, you can find the model tested and the corresponding accuracy.

<center>

<table align= "center">
  <tbody>
  <tr>
    <td align="center">Model</td>
    <td align="center">Logistic Regression</td>
    <td align="center">Random Forest</td>
    <td align="center">Support Vector Machine</td>
    <td align="center">Nearest Neighbors</td>
    <td align="center">Neural Network</td>
  </tr>
  <tr>
    <td align="center">Accuracy</td>
    <td align="center">59.98%</td>
    <td align="center">59.98%</td>
    <td align="center">56.84%</td>
    <td align="center">56.84%</td>
    <td align="center">82.51%</td>
  </tr>
  </tbody>
</table>

As you can see, the Neural Network overperformes the other models. Therefore we decided to select it for the final tool.

## API :outbox_tray:
Next, we created a API, that can be called at [this link](https://www.wolframcloud.com/obj/dario.scalabrin/WebServices/APIRiskRating). You can request data using a POST call, using as parameters what shown below:

```
{
 "Sector"   : string, # Sector in which the company operates
 "Country"  : string, # Country where the company has the HQ
 "CarbInt1" : float,  # Carbon intensity (Scope 1) of the company, expressed in tonnes CO2e/USD mn
 "CarbInt2" : float,  # Carbon intensity (Scope 2) of the company, expressed in tonnes CO2e/USD mn
 "CarbInt3" : float,  # Carbon intensity (Scope 3) of the company, expressed in tonnes CO2e/USD mn
 "CarbDisc" : string, # The way Carbon Intesnisty is calculated by Trucost
 "Revenues" : float   # Revenues of the company, expressed in USD mn
 }

```

## Dashboard :computer:
Finally, we created an interactive dashboard, available at [this link](https://pred-climate-risks.streamlit.app). It has been been built using the [Streamlit](https://streamlit.io) library, and it takes as input a CSV file of a portfolio. The dashboard script calls the Wolfram API (defined in the previous section), it predicts the physical risk of all the companies in the portfolio, and it compute the weighted risk of the portfolio. Next, it shows relevant information of the given portoflio (e.g. summary statistics, distribution, sectorial analysis)

## Authors :technologist:

- [Dario Scalabrin](https://www.linkedin.com/in/scalabrindario/)
- [Jeanne Fernandez](https://www.linkedin.com/in/jeanne-fernandez-0424441b1/)

## License :page_facing_up:
[MIT](https://choosealicense.com/licenses/mit/)
