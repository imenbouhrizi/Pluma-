document.addEventListener("DOMContentLoaded", function () {

    const dashboardData =
        document.getElementById("dashboard-data");

    if (!dashboardData) {
        return;
    }

    const monthLabels =
        JSON.parse(dashboardData.dataset.monthLabels);

    const monthlyIncome =
        JSON.parse(dashboardData.dataset.monthlyIncome);

    const monthlyExpense =
        JSON.parse(dashboardData.dataset.monthlyExpense);

    const pieLabels =
        JSON.parse(dashboardData.dataset.pieLabels);

    const pieValues =
        JSON.parse(dashboardData.dataset.pieValues);

    const pieColors =
        JSON.parse(dashboardData.dataset.pieColors);

    document.querySelectorAll(".legend-dot").forEach(function(dot){
        dot.style.backgroundColor = dot.dataset.color;
    });

    const financialChart =
        document.getElementById("financialChart");

    if (financialChart) {

        new Chart(financialChart, {
            type: "line",

            data: {
                labels: monthLabels,

                datasets: [
                    {
                        label: "Income",
                        data: monthlyIncome,
                        borderColor: "#1DA1F2",
                        backgroundColor: "rgba(29,161,242,0.12)",
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: "Expenses",
                        data: monthlyExpense,
                        borderColor: "#ff00d9",
                        backgroundColor: "rgba(255,0,217,0.08)",
                        fill: false,
                        tension: 0.4
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
                }
            }
        });

    }

    const pieChart =
        document.getElementById("expensePieChart");

    if (pieChart) {

        new Chart(pieChart, {
            type: "doughnut",

            data: {
                labels: pieLabels,

                datasets: [
                    {
                        data: pieValues,
                        backgroundColor: pieColors,
                        borderColor: "#ffffff",
                        borderWidth: 4
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

                cutout: "60%"
            }
        });

    }

});