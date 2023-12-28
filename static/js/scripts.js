document.addEventListener('DOMContentLoaded', function() {

    // Add the event listener for the form submission
    document.getElementById('calculator-form').addEventListener('submit', function(event) {
        event.preventDefault();
        calculate();
    });

    
    // Initialize selectize for the tags input
    $('#ticker').selectize({
        plugins: ['remove_button'],
        delimiter: ',',
        persist: false,
        create: function(input) {
            return {
                value: input,
                text: input
            };
        }
    });

    document.getElementById('submit').click();
});



function loading() {
    // Show loading container on page load
    document.getElementById('loading-container').style.display = 'flex';
}

function hideLoading() {
    // Hide loading container
    document.getElementById('loading-container').style.display = 'none';
}

function calculate() {
    // Show loading container
    loading();

    var selectedTickers = document.getElementById('ticker').value;
    var mos_dcf = document.getElementById('mos_dcf').value;
    var terminal_growth = document.getElementById('terminal_growth').value;
    var discount_rate = document.getElementById('discount_rate').value;
    var conservative_cagr_factor = document.getElementById('conservative_cagr_factor').value;
    var decreasingFcf = document.getElementById('decreasing_fcf').checked;


    var mos_bj = document.getElementById('mos_bj').value;
    var pe_base = document.getElementById('pe_base').value;

    // Make a POST request to the server
    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'ticker': selectedTickers, // Convert array to comma-separated string
            'mos_dcf': mos_dcf,
            'terminal_growth': terminal_growth,
            'discount_rate': discount_rate,
            'conservative_cagr_factor': conservative_cagr_factor,
            'decreasing_fcf': decreasingFcf,
            'mos_bj': mos_bj,
            'pe_base': pe_base,
        }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result-container').innerHTML = data.result_html;
        data.invalid_tickers.forEach(function(ticker) {
            Toastify({
                text: 'Invalid ticker: ' + ticker,
                duration: 3000, // Display duration in milliseconds (e.g., 3000 for 3 seconds)
                close: true,
                gravity: 'top', // toast position: 'top', 'bottom', 'left', 'right'
                position: 'right', // toast position within the gravity: 'left', 'center', 'right'
            }).showToast();
        });
        hideLoading();
    })
    .catch(error => console.error('Error:', error));
}
