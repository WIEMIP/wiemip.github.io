Title: WIEMIP · Updates
Description: The weekly WIEMIP update emails: meetings, paper plans, protocol and data news.

<!-- New week: paste a `## <day> <Month> <year>` block at the top, under the intro,
     then run `uv run --with markdown python updates/build_updates.py`.
     Paste the email verbatim, minus the greeting, sign-off and meeting links. This page
     is public: also leave out passwords, personal email addresses and links to private
     Google docs. -->

# WIEMIP Weekly Updates

A record of emails sent to the WIEMIP community. 

## 20 October 2026

### Upcoming meetings & info

- The WIE special issue is live! It will receive a dedicated SI page once the first preprint is submitted.
- Christina Schädel is leading a permafrost + overshoot meeting on Oct 21 at 2PM UTC

### Protocol/data updates:

- Variable request: If possible, please upload layered soilT along with your model's soil depths.
- 1p5 scenario: We're revising the VL-1p5-CTAP scenario. We’re regenerating the drivers and will have them out by next week. Please hold on running this scenario until the data are finalized.
- WIEMIP registry updates:
    - The package on the hub now supports calculating active layer thickness from model soil temperatures - thanks Remi! Docs [here](/docs/api/wiemip_registry/core.html#calculate_alt). If you have a function that you’d like to add to the package, reach out and we’ll integrate it.
    - I changed days per year from 365.25 to 365. This will have a minor impact on annual sums of flux calculations.
    - The package now includes a standardized colormap for WIEMIP scenario data. Please use it for your analyses. Docs [here](/docs/api/wiemip_registry/const.html#SCENARIO_COLORS).
    - We’ve changed some scenario names from \_cf to \_ctap (constant temperature after peak). This will be changed in the registry in the upcoming days, so be prepared to migrate your scripts.

## 12 October 2026

### Upcoming meetings & info

- Deadline: The next WIEMIP lead author meeting is scheduled for 3PM UTC on October 29th. Lead authors: please come with a zero-order draft (one page with title, structure of the paper, and any figure ideas) to this meeting and be prepared to present in ~3 minutes (with or without a slide)
- Rebecca Varney is leading a Permafrost meeting October 13 at 1PM UTC
- **AGU is coming up**. Please reach out to me if you have WIEMIP-related posters or presentations so I can start tracking them.

### Protocol/data updates:

- Two new future scenarios (VL-CF-PolMIP and VL-1p5-CTAP) are being uploaded to the bucket. Once they're available, please run them if you’re able, and prioritize VL-CF-PolMIP over VL-1p5-CTAP. You should be able to start from historical spinups. These experiments will be very useful as a baseline for overshoot simulations.
- Deadline: Please upload (and QA) all runs by December 1st. This will give the WIEMIP team enough time to validate and reformat the data so analyses can proceed smoothly.
- Modelers: Please upload PFT-level outputs where possible (including the landCoverFrac variable). These data are extremely useful for emulators.

## 5 October 2026

### Upcoming meetings & info

- Juliette Bernard is leading a WIEMIP Non-CO2 GHG meeting tomorrow, Oct 6th, at 1PM UTC
- AGU is coming up. Please reach out to me if you have WIEMIP-related posters or presentations so I can start tracking them.

### Protocol/data updates:

- The progress tracker is now updated automatically with data that’s on the bucket (<https://wiemip.github.io/progress-tracker/>)
- We have the stabilization data generated and will push it to modelers this week or next
- Modelers: If possible, please upload layered soil carbon and rh. These will be very helpful with the Global Soils paper.
    - If you regridded the input data, please upload it as this will save time in postprocessing.

## 28 September 2026

### Upcoming meetings & info

- A WIEMIP global soils meeting will be held on Wed, Sept 30th, at 2PM UTC
- The special collection for WIEMIP will be live in the next few days

### Protocol/data updates:

- We’re going to create a standardized palette for WIEMIP that will be accessible on the Hub - if you have experience with this, or want to provide input, please reach out
- If you would like access to the Hub or WIEMIP data, please reach out - and feel free to share my email with anyone interested
- Modelers: Please provide information on your model’s treatment of fire and PFT composition in the Overleaf document (see email “WIEMIP fire emissions and PFT information”)

## 21 September 2026

### Upcoming meetings & info

- We’ve submitted an EGU session proposal (CL3.1: Warming-Induced Emissions and Earth System Feedbacks: Overshoot, (Ir)Reversibility, and the Carbon Budget) - stay tuned for updates!
- Thomas Gasser is leading a meeting on the ELUC translation paper on Tuesday, Sept 22, at 2PM UTC
- Zhen Zhang is leading a meeting on wetland methane and overshoot on Tuesday, Sept 22, at 3PM UTC
- Thomas Gasser is leading a meeting on warming and SCMs on Friday, Sept 25, at 2PM UTC

### Protocol/data updates:

- The validation page is up-to-date with 1pctCO2 and overshoot submissions (see "WIEMIP validation site" at wiemip.github.io)
- ILAMB data is on the JupyterHub. If you’d like to see any other datasets uploaded, let me know.

## 9 September 2026

### Upcoming meetings & info

- Becky Varney is leading a TCRE follow up meeting on Friday, Sept 11, at 2PM UTC.
- Laura Eifler is leading a fire follow-up meeting on Monday, Sept 14, at 3PM UTC.

### Paper updates:

- I’ve collected a list of model/data leads here (link in the email). I’ve included one team member per modeler for now - please reach out if you’d like to be included in the list.

### Protocol/data updates:

- The recording for the JupyterHub training is in the shared drive (link in the email). Feel free to email me with any questions.
- Monthly aggregates of WIEMIP drivers for analysis are now available on the hub, under wiemip/1pctCO2|overshoot/input/
- We’re still working on the 1.5° scenario - stay tuned

## 3 September 2026

### Upcoming meetings & info

- There is an overshoot conference in Beijing on the 24-25th of November. The abstract deadline is September 6th. See the [website](https://overshootconference.org) for more details. If you’re interested in attending (or already attending) and presenting information on WIEMIP, please reach out to me, Ben Poulter, and Chris Jones.

### Paper updates:

- From Becky Varney: In the 'Global soils' paper we are investigating the sensitivity of biogeochemical fluxes in 1% scenarios and to do this we need RAD simulations, not just COU and BGC. We kindly ask modelling centres to run these additional RAD simulations so we can have the data we need to research this.

### Protocol/data updates:

- We’ve created a [validation site](https://d31938ghkxwp9r.cloudfront.net/) (login in the email) where you can browse WIEMIP data by model and variable. This site relies on the Python package developed to analyze WIEMIP data. I’ve already confirmed weighting methods with most modeling groups. The site will update every night to incorporate new submissions and will populate with more variables as they finish processing.
- Modelers: To support the global soils paper vertically resolved soilC and Rh are important, so if you’re able to supply these please do!

## 31 August 2026

### Upcoming meetings & info:

- Becky Varney is leading a WIEMIP soil carbon meeting on Wednesday, Sept 2, at 2PM UTC.
- Juliette Bernard is leading a meeting on accounting for non-CO2 WIE on Friday, Sept 4, at 1PM UTC.
- The JupyterHub training will take place on Tuesday, Sept 8, at 2PM UTC. We’ll cover how to set it up and how to run simple analyses.

### Paper updates:

- WIEMIP planned analyses and papers are getting traction in the IPCC First Order drafts of Chapters 4, 5, and 9. Please keep up the hard work to get the papers in before the deadline!
- Modelers: Please fill out this table (link in the email) with your model’s details. We’ve added a couple of rows on peatland representation, so if you’ve already filled it out give it a second look.

### Protocol/data updates:

- Model simulation deadline is today (08/31). Thanks all!
- We’re redefining some variables related to methane to make analysis simpler - keep an eye on the data request GitHub page for updates.
- Keep an eye on wiemip.github.io. We’ll put up a site soon where modelers can validate global and regional sums of their data on the fly.

## 24 August 2026

The August 31st simulation deadline is fast approaching, so please submit data!

### Upcoming meetings & info:

- Shania will be reaching out to paper leads to coordinate tracking in a new spreadsheet. Going forward, please CC me, Shania and Ben on paper planning emails.
- Please fill out this [when2meet](https://www.when2meet.com/?38092116-bX42o) if you’re interested in a training session for the WIEMIP JupyterHub.

### Paper updates:

- We’re planning to include an announcement on the WIEMIP list of planned papers in an upcoming CMIP Digest. AerChemMIP and RFMIP included a list of their planned articles, analyses, and authors in the last Digest. We thought this would be a good opportunity to advertise WIEMIP. Please reach out to me if you’d like your paper idea excluded from the Digest.
- Zhen Zhang will be leading a paper on the responses of wetland methane to overshoot. Please reach out to him if you’re interested in joining a planning meeting the week of September 7th.

### Protocol/data updates:

- I’ve put together some documentation on the JupyterHub [here](/docs/api/wiemip_registry.html). Please raise an issue in the [associated GitHub repository](https://github.com/WIEMIP/wiemip-data-registry/issues) if you run into any issues.
- CLM-FATES, ORCHIDEE, and LPJ-GUESS’s overshoot results will be ready mid-Sept.
- We’re still working on the 1.5° stabilization scenario - stay tuned.

## 17 August 2026

The August 31 simulation deadline is fast approaching, so please submit data if possible!

### Upcoming meetings:

- Joe Clarke is leading a meeting on progress for the Overshoot group tomorrow (2026/08/18) at 9AM MDT/3UTC. Please reach out to him if you'd like to join.

### Protocol/data updates:

- Some models have revised their methane output and re-uploaded to the Wasabi bucket. Anyone doing analyses with methane fluxes should re-download or use overwrite=True with functions on the JupyterHub.
- **Modelers:** Juliette Bernard and I have reached out regarding validation of methane/n2o and land carbon stock, respectively. Please respond to these emails at your earliest convenience. If you have suggestions on how to better manage data QA/QC, please email me.
