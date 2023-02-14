# NanoWeb Main
## This is the main repository for NanoWeb.

### Installation
    Requirements listed in requirements.txt in main directory. 
    1. Run pip -r requirements.txt in a terminal window.
    2. in a terminal window, type "streamlit run NanoPrepare.py".
    3. NanoWeb should open in your default browser.
### Uninstallation
    Delete the SH32 main directory in your filesystem.
### File input
    accepted files are currently zip directories of any number of .txt experiments
    for instance an optics11 d mode zipped ddirectory containing one file, 
    a ".txt" file, with relevant header to the filetype followed by data.
### JSON output (not working)
    not working - first click save to json, then download JSON file, JSON as test.json will be downloaded to your downloads folder.
### Features of NanoWeb Prepare 

	Users can apply filters from a drop down menu on the bottom left.	

	Users can crop the range of displacement shown with the sliders on the right.
    
    Users can zoom into and hover over a datapoint to read the Force, Displacement and experiment file location of said datapoint.	

	Users can export to JSON for use in NanoWeb Analysis or similar.
### Known issues in NanoWeb Prepare

    Tooltip hitboxes are too small, making it difficult to hover over a datapoint.

    Zooming in and out is not smooth.
    
    Exporting to JSON is not working.
### Features of NanoWeb Analysis

    Users can upload a JSON file from NanoWeb Prepare or similar.

    Users can select a file from the JSON file to view.

    Users can select a range of files from the JSON file to view.
### Known issues in NanoWeb Analysis

    GUI scale and usability is poor.
    
    Loading time is poor for json files which contain a large number of experiments.

    Analysis tools are not implemented.

    Exporting a process log is not implemented.