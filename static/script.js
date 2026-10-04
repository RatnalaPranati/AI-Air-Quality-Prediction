let aqiChart = null;


// ============================================================
// SEARCH CITY
// ============================================================

async function searchCity() {

    const input = document.getElementById("cityInput");

    const city = input.value.trim();

    const errorMessage =
        document.getElementById("errorMessage");

    const button =
        document.getElementById("searchButton");

    const searchText =
        document.getElementById("searchText");

    const spinner =
        document.getElementById("loadingSpinner");


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!city) {

        errorMessage.textContent =
            "Please enter a city name.";

        return;

    }


    // --------------------------------------------------------
    // LOADING STATE
    // --------------------------------------------------------

    errorMessage.textContent = "";

    button.disabled = true;

    searchText.classList.add("hidden");

    spinner.classList.remove("hidden");


    try {

        const response = await fetch(
            `/api/air-quality?city=${encodeURIComponent(city)}`
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                "Unable to retrieve air quality data."
            );

        }


        // ----------------------------------------------------
        // DISPLAY RESULTS
        // ----------------------------------------------------

        displayResults(data);


    } catch (error) {

        console.error(error);

        errorMessage.textContent =
            error.message ||
            "Something went wrong. Please try again.";

        document
            .getElementById("results")
            .classList.add("hidden");


    } finally {

        button.disabled = false;

        searchText.classList.remove("hidden");

        spinner.classList.add("hidden");

    }

}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(data) {

    const results =
        document.getElementById("results");

    const welcome =
        document.getElementById("welcome");


    results.classList.remove("hidden");

    welcome.classList.add("hidden");


    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const location =
        data.location;

    document.getElementById(
        "locationName"
    ).textContent =
        `${location.city}, ${location.country}`;


    document.getElementById(
        "coordinates"
    ).textContent =
        `Lat ${Number(location.latitude).toFixed(4)}
         • Lon ${Number(location.longitude).toFixed(4)}`;


    // --------------------------------------------------------
    // CURRENT AQI
    // --------------------------------------------------------

    const current =
        data.current;

    document.getElementById(
        "currentAQI"
    ).textContent =
        formatNumber(current.aqi);


    document.getElementById(
        "currentCategory"
    ).textContent =
        current.category;


    document.getElementById(
        "mainPollutant"
    ).textContent =
        current.main_pollutant;


    // Apply AQI level
    setAQILevel(
        document.getElementById("currentCard"),
        current.level
    );


    // --------------------------------------------------------
    // PREDICTION
    // --------------------------------------------------------

    const prediction =
        data.prediction;


    document.getElementById(
        "predictedAQI"
    ).textContent =
        formatNumber(prediction.aqi);


    document.getElementById(
        "predictedCategory"
    ).textContent =
        prediction.category;


    const difference =
        prediction.difference;


    const differenceElement =
        document.getElementById(
            "predictionDifference"
        );


    if (difference > 0) {

        differenceElement.textContent =
            `↑ ${Math.abs(difference)} AQI`;

    } else if (difference < 0) {

        differenceElement.textContent =
            `↓ ${Math.abs(difference)} AQI`;

    } else {

        differenceElement.textContent =
            "No significant change";

    }


    // --------------------------------------------------------
    // POLLUTANTS
    // --------------------------------------------------------

    const pollutants =
        current.pollutants;


    setText(
        "pm25",
        pollutants.pm2_5
    );


    setText(
        "pm10",
        pollutants.pm10
    );


    setText(
        "co",
        pollutants.carbon_monoxide
    );


    setText(
        "no2",
        pollutants.nitrogen_dioxide
    );


    setText(
        "so2",
        pollutants.sulphur_dioxide
    );


    setText(
        "o3",
        pollutants.ozone
    );


    // --------------------------------------------------------
    // WEATHER
    // --------------------------------------------------------

    const weather =
        data.weather;


    setText(
        "temperature",
        weather.temperature
    );


    setText(
        "humidity",
        weather.humidity
    );


    setText(
        "windSpeed",
        weather.wind_speed
    );


    // --------------------------------------------------------
    // AI ANALYSIS
    // --------------------------------------------------------

    document.getElementById(
        "analysisAQI"
    ).textContent =
        formatNumber(prediction.aqi);


    document.getElementById(
        "analysisTitle"
    ).textContent =
        generateAnalysisTitle(
            current.aqi,
            prediction.aqi
        );


    document.getElementById(
        "analysisMessage"
    ).textContent =
        generateAnalysisMessage(
            current.aqi,
            prediction.aqi,
            current.main_pollutant
        );


    // --------------------------------------------------------
    // RECOMMENDATION
    // --------------------------------------------------------

    document.getElementById(
        "recommendationTitle"
    ).textContent =
        data.recommendation.title;


    document.getElementById(
        "recommendationMessage"
    ).textContent =
        data.recommendation.message;


    // --------------------------------------------------------
    // CHART
    // --------------------------------------------------------

    createAQIChart(data.trend);


    // --------------------------------------------------------
    // SCROLL
    // --------------------------------------------------------

    setTimeout(() => {

        results.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);

}


// ============================================================
// AQI LEVEL
// ============================================================

function setAQILevel(element, level) {

    element.classList.remove(
        "aqi-good",
        "aqi-moderate",
        "aqi-sensitive",
        "aqi-unhealthy",
        "aqi-very-unhealthy",
        "aqi-hazardous"
    );


    element.classList.add(
        `aqi-${level}`
    );

}


// ============================================================
// NUMBER FORMAT
// ============================================================

function formatNumber(value) {

    if (
        value === null ||
        value === undefined ||
        isNaN(value)
    ) {

        return "--";

    }


    return Number(value).toFixed(1);

}


// ============================================================
// SET TEXT
// ============================================================

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (
        value === null ||
        value === undefined ||
        isNaN(value)
    ) {

        element.textContent = "--";

        return;

    }


    element.textContent =
        Number(value).toFixed(1);

}


// ============================================================
// AI ANALYSIS TITLE
// ============================================================

function generateAnalysisTitle(
    currentAQI,
    predictedAQI
) {

    const difference =
        predictedAQI - currentAQI;


    if (difference > 10) {

        return "Air quality may deteriorate.";

    }


    if (difference < -10) {

        return "Air quality may improve.";

    }


    return "Air quality is expected to remain relatively stable.";

}


// ============================================================
// AI ANALYSIS MESSAGE
// ============================================================

function generateAnalysisMessage(
    currentAQI,
    predictedAQI,
    pollutant
) {

    const difference =
        predictedAQI - currentAQI;


    if (difference > 10) {

        return (
            `The machine learning model predicts an increase ` +
            `in AQI during the next hour. ${pollutant} is currently ` +
            `identified as the main pollutant. Consider reducing ` +
            `prolonged outdoor exposure.`
        );

    }


    if (difference < -10) {

        return (
            `The machine learning model predicts a decrease ` +
            `in AQI during the next hour. Current air quality ` +
            `conditions may improve slightly.`
        );

    }


    return (
        `The machine learning model predicts that AQI will ` +
        `remain relatively close to the current level during ` +
        `the next hour. ${pollutant} is currently identified ` +
        `as the main pollutant.`
    );

}


// ============================================================
// AQI CHART
// ============================================================

function createAQIChart(trend) {

    const canvas =
        document.getElementById("aqiChart");


    if (!canvas) {
        return;
    }


    const labels =
        trend.map(item =>
            formatTime(item.time)
        );


    const values =
        trend.map(item =>
            item.aqi
        );


    if (aqiChart) {

        aqiChart.destroy();

    }


    aqiChart =
        new Chart(canvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {

                        label: "AQI",

                        data: values,

                        borderWidth: 3,

                        tension: 0.35,

                        pointRadius: 2,

                        pointHoverRadius: 6,

                        fill: true,

                        backgroundColor:
                            "rgba(15, 118, 110, 0.08)",

                        borderColor:
                            "#0f766e"

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        display: false

                    }

                },

                scales: {

                    x: {

                        grid: {

                            display: false

                        },

                        ticks: {

                            maxTicksLimit: 8,

                            color: "#687572"

                        }

                    },

                    y: {

                        beginAtZero: true,

                        grid: {

                            color: "#edf2f0"

                        },

                        ticks: {

                            color: "#687572"

                        }

                    }

                }

            }

        });

}


// ============================================================
// FORMAT TIME
// ============================================================

function formatTime(timeString) {

    try {

        const date =
            new Date(timeString);


        return date.toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );

    } catch {

        return timeString;

    }

}


// ============================================================
// ENTER KEY
// ============================================================

document
    .getElementById("cityInput")
    .addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Enter") {

                searchCity();

            }

        }
    );