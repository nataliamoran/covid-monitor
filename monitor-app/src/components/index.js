import React from 'react';
import './styles.css';
import axios from 'axios';
import {DATES, FILTER,} from "../config";


class Monitor extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            titles: [],
            countries: [],
            provinces_states: [],
            combined_keys: [],
            date_from: "",
            date_to: "",
            format: "",
            download_button: null,
            csv_file: null,
            filtered_data: null,
            csv_upload_status: null,
        };

        this.updateTitles = this.updateTitles.bind(this);
        this.updateCountries = this.updateCountries.bind(this);
        this.updateProvinces = this.updateProvinces.bind(this);
        this.updateCombinedKeys = this.updateCombinedKeys.bind(this);
        this.updateDateFrom = this.updateDateFrom.bind(this);
        this.updateDateTo = this.updateDateTo.bind(this);
        this.updateFormat = this.updateFormat.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    downloadFile = ({data, fileName, fileType}) => {
        // code snippet is taken from https://theroadtoenterprise.com/blog/how-to-download-csv-and-json-files-in-react
        const blob = new Blob([data], {type: fileType})
        const a = document.createElement('a')
        a.download = fileName
        a.href = window.URL.createObjectURL(blob)
        const clickEvt = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true,
        })
        a.dispatchEvent(clickEvt)
        a.remove()
    }

    createJson = e => {
        e.preventDefault()
        this.downloadFile({
            data: JSON.stringify(this.state.filtered_data),
            fileName: 'dates.json',
            fileType: 'text/json',
        })
        this.setState({download_button: null});
    }

    createCsv = e => {
        e.preventDefault()
        this.downloadFile({
            data: this.state.filtered_data,
            fileName: 'dates.csv',
            fileType: 'text/csv',
        })
        this.setState({download_button: null});
    }

    onCsvChange = event => {
        this.setState({csv_file: event.target.files[0]});
    };

    onCsvUpload = () => {
        const requestData = new FormData();
        requestData.append(
            "csv_file",
            this.state.csv_file,
            this.state.csv_file.name
        );
        this.setState({csv_upload_status: "process",});
        this.forceUpdate();
        axios.post(DATES, requestData)
            .then((response) => {
                this.setState({
                    csv_upload_status: "success",
                });
                this.forceUpdate();
            })
            .catch((error) => {
                this.setState({
                    csv_upload_status: "failure",
                });
                this.forceUpdate();
            });
        setTimeout(function () {
            this.setState({csv_upload_status: null,})
        }.bind(this), 10000)
    };

    updateTitles(event) {
        this.setState({titles: event.target.value.split(',')});
    }

    updateCountries(event) {
        this.setState({countries: event.target.value.split(',')});
    }

    updateProvinces(event) {
        this.setState({provinces_states: event.target.value.split(',')});
    }

    updateCombinedKeys(event) {
        this.setState({combined_keys: event.target.value});
    }

    updateDateFrom(event) {
        this.setState({date_from: event.target.value});
    }

    updateDateTo(event) {
        this.setState({date_to: event.target.value});
    }

    updateFormat(event) {
        this.setState({format: event.target.value});
    }

    handleSubmit(event) {
        const request = {
            "titles": this.state.titles,
            "countries": this.state.countries,
            "provinces_states": this.state.provinces_states,
            "combined_keys": this.state.combined_keys.split('&'),
            "date_from": this.state.date_from,
            "date_to": this.state.date_to,
            "format": this.state.format ? this.state.format : "JSON",
        }
        const requestDates = {
            method: 'POST',
            body: JSON.stringify(request),
            headers: {
                'Content-Type': 'application/json'
            }
        };
        fetch(FILTER, requestDates)
            .then((response) => response.json())
            .then((json) => {
                this.setState({
                    filtered_data: json,
                    download_button: request["format"],
                    titles: [],
                    countries: [],
                    provinces_states: [],
                    combined_keys: [],
                    date_from: "",
                    date_to: "",
                    format: "",
                });
                this.forceUpdate();
            })
            .catch(() => {
            });
        event.preventDefault();
    }

    render() {
        let downloadButton;
        let uploadStatus;

        if (this.state.csv_upload_status && this.state.csv_upload_status === "success") {
            uploadStatus = (
                <p className="success">
                    CSV File is successfully uploaded.
                </p>
            )
        } else if (this.state.csv_upload_status && this.state.csv_upload_status === "process") {
            uploadStatus = (
                <p className="in_process">
                    CSV file is uploading. Please wait.
                </p>
            )
        } else if (this.state.csv_upload_status && this.state.csv_upload_status === "failure") {
            uploadStatus = (
                <p className="failure">
                    Sorry, something went wrong. File failed to upload.
                </p>
            )
        }

        if (this.state.download_button && this.state.download_button === "CSV") {
            downloadButton = (
                <button className="button" type='button' onClick={this.createCsv}>
                    Download CSV
                </button>
            );
        } else if (this.state.download_button && this.state.download_button === "JSON") {
            downloadButton = (
                <button className="button" type='button' onClick={this.createJson}>
                    Download JSON
                </button>

            );
        }

        return (
            <div className="app">
                <h1 className="title">
                    COVID-19 Monitor
                </h1>
                <h2 className="title">
                    Upload CSV
                </h2>
                <div>
                    <input type="file" onChange={this.onCsvChange}/>
                    <button className="button" onClick={this.onCsvUpload}>
                        Save
                    </button>
                    {uploadStatus}
                </div>
                <h2 className="title">
                    Query Data
                </h2>
                <div>
                    <form onSubmit={this.handleSubmit}>
                        <div className="label">
                            <label>
                                <span className="label_description"> Cases: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.titles}
                                       placeholder={"deaths,confirmed,active,recovered"}
                                       onChange={this.updateTitles}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Countries: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.countries}
                                       placeholder={"Algeria,US"}
                                       onChange={this.updateCountries}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Provinces / States: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.provinces_states}
                                       placeholder={"Alabama,California"}
                                       onChange={this.updateProvinces}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Combined Keys: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.combined_keys}
                                       placeholder={"Autauga, Alabama, US&Ventura, California, US"}
                                       onChange={this.updateCombinedKeys}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Date from: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.date_from}
                                       placeholder={"01/20/21"}
                                       onChange={this.updateDateFrom}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Date to: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.date_to}
                                       placeholder={"01/20/21"}
                                       onChange={this.updateDateTo}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Format (JSON or CSV): </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.format}
                                       placeholder={"JSON"}
                                       onChange={this.updateFormat}/>
                            </label>
                        </div>
                        <input className="button" type="submit" value="Submit"/>
                    </form>
                    <div>
                        {downloadButton}
                    </div>
                </div>
            </div>
        );
    }
}

export default Monitor;