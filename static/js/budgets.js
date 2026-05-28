console.log("budgets.js chargé");
function openModalById(id){
    const modal = document.getElementById(id);
    if(modal){
        modal.style.display = "flex";
    }
}

function closeModalById(id){
    const modal = document.getElementById(id);
    if(modal){
        modal.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function(){

    const openBudgetBtn = document.querySelector(".open-budget-modal");
    const closeBudgetBtn = document.querySelector(".close-budget-modal");

    const openCategoryBtn = document.querySelector(".open-category-modal");
    const closeCategoryBtn = document.querySelector(".close-category-modal");

    const openAdjustBtn = document.querySelector(".open-adjust-modal");
    const closeAdjustBtn = document.querySelector(".close-adjust-modal");

    const closeEditBudgetBtn = document.querySelector(".close-edit-budget-modal");
    const editBudgetBtns = document.querySelectorAll(".open-edit-budget-modal");

    if(openBudgetBtn){
        openBudgetBtn.addEventListener("click", function(){
            openModalById("budgetModal");
        });
    }

    if(closeBudgetBtn){
        closeBudgetBtn.addEventListener("click", function(){
            closeModalById("budgetModal");
        });
    }

    if(openCategoryBtn){
        openCategoryBtn.addEventListener("click", function(){
            openModalById("categoryModal");
        });
    }

    if(closeCategoryBtn){
        closeCategoryBtn.addEventListener("click", function(){
            closeModalById("categoryModal");
        });
    }

    if(openAdjustBtn){
        openAdjustBtn.addEventListener("click", function(){
            openModalById("adjustModal");
        });
    }

    if(closeAdjustBtn){
        closeAdjustBtn.addEventListener("click", function(){
            closeModalById("adjustModal");
        });
    }

    if(closeEditBudgetBtn){
        closeEditBudgetBtn.addEventListener("click", function(){
            closeModalById("editBudgetModal");
        });
    }

    ["budgetModal", "categoryModal", "adjustModal", "editBudgetModal"].forEach(function(id){
        const modal = document.getElementById(id);

        if(modal){
            modal.addEventListener("click", function(e){
                if(e.target === modal){
                    closeModalById(id);
                }
            });
        }
    });

    editBudgetBtns.forEach(function(btn){
        btn.addEventListener("click", function(){

            const budgetId = this.dataset.id;
            const form = document.getElementById("editBudgetForm");

            if(form){
                form.action = "/budgets/edit/" + budgetId;
            }

            document.getElementById("edit_name").value = this.dataset.name || "";
            document.getElementById("edit_total_amount").value = this.dataset.total || "";
            document.getElementById("edit_spent_amount").value = this.dataset.spent || "";
            document.getElementById("edit_currency").value = this.dataset.currency || "EUR";
            document.getElementById("edit_start_date").value = this.dataset.startDate || "";
            document.getElementById("edit_end_date").value = this.dataset.endDate || "";

            const categoryId = this.dataset.categoryId || "";
            const categoryRadios = document.querySelectorAll(".edit-category-radio");

            categoryRadios.forEach(function(radio){
                radio.checked = radio.value === categoryId;
            });

            openModalById("editBudgetModal");
        });
    });

    const colorInput = document.querySelector('input[name="color"]');
    const iconLabels = document.querySelectorAll(".icon-catalog label");

    function updateIconColor(color){
        iconLabels.forEach(function(label){
            label.style.setProperty("--selected-color", color);
        });
    }

    if(colorInput){
        updateIconColor(colorInput.value);

        colorInput.addEventListener("input", function(){
            updateIconColor(this.value);
        });
    }

});