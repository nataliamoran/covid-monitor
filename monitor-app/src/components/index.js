import React from 'react';
import './styles.css';
import axios from 'axios';
import {DATES, FILTER, DELETE,} from "../config";


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
            json_offset: null,
            json_limit: null,
            download_button: null,
            csv_file: null,
            filtered_data: null,
            csv_upload_status: null,
            delete_all_status: null,
            filter_status: null,
        };

        this.updateTitles = this.updateTitles.bind(this);
        this.updateCountries = this.updateCountries.bind(this);
        this.updateProvinces = this.updateProvinces.bind(this);
        this.updateCombinedKeys = this.updateCombinedKeys.bind(this);
        this.updateDateFrom = this.updateDateFrom.bind(this);
        this.updateDateTo = this.updateDateTo.bind(this);
        this.updateFormat = this.updateFormat.bind(this);
        this.updateJsonLimit = this.updateJsonLimit.bind(this);
        this.updateJsonOffset = this.updateJsonOffset.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleDeleteAll = this.handleDeleteAll.bind(this);
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
                if (response.status === 201) {
                    this.setState({
                        csv_upload_status: "success",
                    });
                    this.forceUpdate();
                    setTimeout(function () {
                        this.setState({csv_upload_status: null,})
                    }.bind(this), 10000)
                } else {
                    this.setState({
                        csv_upload_status: "large-file",
                    });
                    this.forceUpdate();
                    setTimeout(function () {
                        this.setState({csv_upload_status: null,})
                    }.bind(this), 60000 * 15)
                }

            })
            .catch((error) => {
                this.setState({
                    csv_upload_status: "failure",
                });
                this.forceUpdate();
                setTimeout(function () {
                    this.setState({csv_upload_status: null,})
                }.bind(this), 10000)
            });
    };

    updateTitles(event) {
        this.setState({titles: event.target.value});
    }

    updateCountries(event) {
        this.setState({countries: event.target.value});
    }

    updateProvinces(event) {
        this.setState({provinces_states: event.target.value});
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

    updateJsonLimit(event) {
        this.setState({json_limit: event.target.value});
    }

    updateJsonOffset(event) {
        this.setState({json_offset: event.target.value});
    }

    handleDeleteAll(event) {
        const data = {
            method: 'DELETE'
        };
        fetch(DELETE, data)
            .then((response) => {
                this.setState({
                    delete_all_status: 1,
                });
                this.forceUpdate();
                setTimeout(function () {
                    this.setState({delete_all_status: null,})
                }.bind(this), 5000)
            })
            .catch(() => {
            });
        event.preventDefault();
    }

    handleSubmit(event) {
        let request = {
            "titles": this.state.titles,
            "countries": this.state.countries,
            "provinces_states": this.state.provinces_states,
            "combined_keys": this.state.combined_keys,
            "date_from": this.state.date_from,
            "date_to": this.state.date_to,
            "format": this.state.format ? this.state.format : "JSON",
        };
        if (typeof request["titles"] === 'string') {
            request["titles"] = request["titles"].split("&");
        }
        if (typeof request["countries"] === 'string') {
            request["countries"] = request["countries"].split("&");
        }
        if (typeof request["provinces_states"] === 'string') {
            request["provinces_states"] = request["provinces_states"].split("&");
        }
        if (typeof request["combined_keys"] === 'string') {
            request["combined_keys"] = request["combined_keys"].split("&");
        }
        const requestDates = {
            method: 'POST',
            body: JSON.stringify(request),
            headers: {
                'Content-Type': 'application/json'
            }
        };

        let requestUrl;
        if (request["format"] === "JSON"){
            requestUrl = FILTER + '?limit=' + this.state.json_limit + '&offset=' + this.state.json_offset;
        } else {
            requestUrl = FILTER;
        }

        this.setState({filter_status: "process",});
        this.forceUpdate();
        fetch(requestUrl, requestDates)
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
                    json_limit: null,
                    json_offset: null,
                    format: "",
                    filter_status: null
                });
                this.forceUpdate();
            })
            .catch(() => {
                this.setState({
                    filter_status: "failure",
                });
                this.forceUpdate();
                setTimeout(function () {
                    this.setState({filter_status: null,})
                }.bind(this), 10000)
            });
        event.preventDefault();
    }

    render() {
        let downloadButton;
        let uploadStatus;
        let deleteStatus;
        let filterFailedStatus;

        if (this.state.filter_status && this.state.filter_status === "failure") {
            filterFailedStatus = (
                <p className="failure">
                    Your request cannot be processed. Please make sure your input follows the format shown by form field
                    placeholders.
                </p>
            )
        } else if (this.state.filter_status && this.state.filter_status === "process") {
            filterFailedStatus = (
                <p className="in_process">
                    Your request is being processed - please wait.
                </p>
            )
        }

        if (this.state.delete_all_status && this.state.delete_all_status === 1) {
            deleteStatus = (
                <p className="success">
                    All data is successfully deleted from the database.
                </p>
            )
        }

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
        } else if (this.state.csv_upload_status && this.state.csv_upload_status === "large-file") {
            uploadStatus = (
                <p className="in_process">
                    You uploaded a large file. Processing this file can take up to 10-15 minutes. Please wait.
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
                                       placeholder={"deaths&confirmed&active&recovered"}
                                       onChange={this.updateTitles}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Countries: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.countries}
                                       placeholder={"Algeria&US"}
                                       onChange={this.updateCountries}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> Provinces / States: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.provinces_states}
                                       placeholder={"Alabama&California"}
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
                        <div className="label">
                            <label>
                                <span className="label_description"> JSON Limit: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.json_limit}
                                       placeholder={"100"}
                                       onChange={this.updateJsonLimit}/>
                            </label>
                        </div>
                        <div className="label">
                            <label>
                                <span className="label_description"> JSON Offset: </span>
                                <input type="text"
                                       className="text_input"
                                       value={this.state.json_offset}
                                       placeholder={"0"}
                                       onChange={this.updateJsonOffset}/>
                            </label>
                        </div>
                        <input className="button" type="submit" value="Submit"/>
                    </form>
                    <div>
                        {filterFailedStatus}
                    </div>
                    <div>
                        {downloadButton}
                    </div>
                </div>
                <h2 className="title">
                    Delete All Data
                </h2>
                <div>
                    <button className="button" onClick={this.handleDeleteAll}>
                        Delete All
                    </button>
                    <div>
                        {deleteStatus}
                    </div>
                </div>
            </div>
        );
    }
}

export default Monitor;