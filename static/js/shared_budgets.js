document.addEventListener("DOMContentLoaded", function(){

    const sharedModal = document.getElementById("sharedBudgetModal");
    const membersModal = document.getElementById("membersModal");
    const editSharedModal = document.getElementById("editSharedBudgetModal");
    const viewModal = document.getElementById("viewBudgetModal");
    const expenseModal = document.getElementById("expenseModal");
    const editExpenseModal = document.getElementById("editExpenseModal");

    const openSharedBtn = document.querySelector(".open-shared-modal");
    const closeSharedBtn = document.querySelector(".close-shared-modal");

    const closeMembersBtn = document.querySelector(".close-members-modal");
    const openMembersBtns = document.querySelectorAll(".open-members-modal");

    const openEditSharedBtns = document.querySelectorAll(".open-edit-shared-modal");
    const closeEditSharedBtn = document.querySelector(".close-edit-shared-modal");

    const openViewBtns = document.querySelectorAll(".open-view-modal");
    const closeViewBtn = document.querySelector(".close-view-modal");

    const openExpenseBtns = document.querySelectorAll(".open-expense-modal");
    const closeExpenseBtn = document.querySelector(".close-expense-modal");
    const expenseForm = document.getElementById("expenseForm");
    const categorySelect = document.getElementById("expenseCategorySelect");

    const openEditExpenseBtns = document.querySelectorAll(".open-edit-expense-modal");
    const closeEditExpenseBtn = document.querySelector(".close-edit-expense-modal");
    const editExpenseForm = document.getElementById("editExpenseForm");
    const editExpenseCategorySelect = document.getElementById("editExpenseCategorySelect");

    function openModal(modal){
        if(modal){
            modal.style.display = "flex";
        }
    }

    function closeModal(modal){
        if(modal){
            modal.style.display = "none";
        }
    }

    if(openSharedBtn){
        openSharedBtn.addEventListener("click", function(){
            openModal(sharedModal);
        });
    }

    if(closeSharedBtn){
        closeSharedBtn.addEventListener("click", function(){
            closeModal(sharedModal);
        });
    }

    openMembersBtns.forEach(function(btn){
        btn.addEventListener("click", function(){
            const budgetId = this.dataset.budgetId;

            document.querySelectorAll(".members-section").forEach(function(section){
                section.style.display = "none";
            });

            const activeSection = document.querySelector(
                '.members-section[data-budget-id="' + budgetId + '"]'
            );

            if(activeSection){
                activeSection.style.display = "block";
            }

            openModal(membersModal);
        });
    });

    if(closeMembersBtn){
        closeMembersBtn.addEventListener("click", function(){
            closeModal(membersModal);
        });
    }

    openEditSharedBtns.forEach(function(btn){
        btn.addEventListener("click", function(){
            const id = this.dataset.id;

            const categories = this.dataset.categories
                ? this.dataset.categories.split(",")
                : [];

            document.getElementById("editSharedBudgetForm").action =
                "/budgets/shared/edit/" + id;

            document.getElementById("edit_shared_name").value = this.dataset.name || "";
            document.getElementById("edit_shared_total").value = this.dataset.total || "";
            document.getElementById("edit_shared_currency").value = this.dataset.currency || "EUR";
            document.getElementById("edit_shared_start").value = this.dataset.startDate || "";
            document.getElementById("edit_shared_end").value = this.dataset.endDate || "";

            document.querySelectorAll(".edit-shared-category").forEach(function(input){
                input.checked = categories.includes(input.value);
            });

            openModal(editSharedModal);
        });
    });

    if(closeEditSharedBtn){
        closeEditSharedBtn.addEventListener("click", function(){
            closeModal(editSharedModal);
        });
    }

    openViewBtns.forEach(function(btn){
        btn.addEventListener("click", function(){
            const budgetId = this.dataset.budgetId;

            document.querySelectorAll(".view-budget-section").forEach(function(section){
                section.style.display = "none";
            });

            const activeSection = document.querySelector(
                '.view-budget-section[data-budget-id="' + budgetId + '"]'
            );

            if(activeSection){
                activeSection.style.display = "block";
            }

            openModal(viewModal);
        });
    });

    if(closeViewBtn){
        closeViewBtn.addEventListener("click", function(){
            closeModal(viewModal);
        });
    }

    openExpenseBtns.forEach(function(btn){
        btn.addEventListener("click", function(){
            const budgetId = this.dataset.budgetId;
            const categories = this.dataset.categories;

            if(expenseForm){
                expenseForm.action = "/budgets/shared/add-expense/" + budgetId;
            }

            if(categorySelect){
                categorySelect.innerHTML = "";

                if(categories){
                    categories.split("||").forEach(function(item){
                        const data = item.split("::");

                        if(data.length === 2){
                            const option = document.createElement("option");
                            option.value = data[0];
                            option.textContent = data[1];
                            categorySelect.appendChild(option);
                        }
                    });
                }
            }

            openModal(expenseModal);
        });
    });

    if(closeExpenseBtn){
        closeExpenseBtn.addEventListener("click", function(){
            closeModal(expenseModal);
        });
    }

    openEditExpenseBtns.forEach(function(btn){
        btn.addEventListener("click", function(){

            const expenseId = this.dataset.expenseId;
            const categories = this.dataset.categories;

            if(editExpenseForm){
                editExpenseForm.action =
                    "/budgets/shared/edit-expense/" + expenseId;
            }

            document.getElementById("edit_expense_name").value =
                this.dataset.name || "";

            document.getElementById("edit_expense_amount").value =
                this.dataset.amount || "";

            if(editExpenseCategorySelect){
                editExpenseCategorySelect.innerHTML = "";

                if(categories){
                    categories.split("||").forEach(function(item){
                        const data = item.split("::");

                        if(data.length === 2){
                            const option = document.createElement("option");
                            option.value = data[0];
                            option.textContent = data[1];

                            if(data[0] === btn.dataset.categoryId){
                                option.selected = true;
                            }

                            editExpenseCategorySelect.appendChild(option);
                        }
                    });
                }
            }

            openModal(editExpenseModal);
        });
    });

    if(closeEditExpenseBtn){
        closeEditExpenseBtn.addEventListener("click", function(){
            closeModal(editExpenseModal);
        });
    }

    [
        sharedModal,
        membersModal,
        editSharedModal,
        viewModal,
        expenseModal,
        editExpenseModal
    ].forEach(function(modal){
        if(modal){
            modal.addEventListener("click", function(e){
                if(e.target === modal){
                    closeModal(modal);
                }
            });
        }
    });

    const dataElement = document.getElementById("shared-budget-data");
    const openMembersId = dataElement ? dataElement.dataset.openMembers : "";

    if(openMembersId){
        document.querySelectorAll(".members-section").forEach(function(section){
            section.style.display = "none";
        });

        const activeSection = document.querySelector(
            '.members-section[data-budget-id="' + openMembersId + '"]'
        );

        if(activeSection){
            activeSection.style.display = "block";
            openModal(membersModal);
        }
    }

});