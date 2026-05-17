document.addEventListener("DOMContentLoaded", function () {

    const pieCanvas = document.getElementById("expensePieChart");
    const financialCanvas = document.getElementById("financialChart");

    console.log("Pie:", pieCanvas);
    console.log("Financial:", financialCanvas);

    if (pieCanvas) {
        new Chart(pieCanvas, {
            type: "pie",
            data: {
                labels: ["Entertainment", "Bill Expense", "Others", "Investment"],
                datasets: [{
                    data: [30, 15, 35, 20],
                    backgroundColor: ["#303765", "#ff7a00", "#1d19ff", "#ff00e5"],
                    borderColor: "#ffffff",
                    borderWidth: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    if (financialCanvas) {
        new Chart(financialCanvas, {
            type: "line",
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"],
                datasets: [
                    {
                        label: "Income",
                        data: [0, 1400, 900, 2200, 1000, 1100, 1400, 2800, 2200, 3600, 5000, 3200],
                        borderColor: "#169ff3",
                        backgroundColor: "rgba(22,159,243,0.20)",
                        fill: true,
                        tension: 0.45
                    },
                    {
                        label: "Expenses",
                        data: [1600, 500, 400, 350, 1600, 1700, 2300, 800, 700, 2500, 2200, 5000],
                        borderColor: "#ff00ff",
                        backgroundColor: "transparent",
                        fill: false,
                        tension: 0.45
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

});