document.addEventListener("DOMContentLoaded", function(){

    const transactionModal =
        document.getElementById("transactionModal");

    const editTransactionModal =
        document.getElementById("editTransactionModal");

    const cardModal =
        document.getElementById("cardModal");

    const openTransactionBtn =
        document.querySelector(".open-transaction-modal");

    const closeTransactionBtn =
        document.querySelector(".close-transaction-modal");

    const openCardBtn =
        document.querySelector(".open-card-modal");

    const closeCardBtn =
        document.querySelector(".close-card-modal");

    const openEditTransactionBtns =
        document.querySelectorAll(".open-edit-transaction-modal");

    const closeEditTransactionBtn =
        document.querySelector(".close-edit-transaction-modal");

    const editTransactionForm =
        document.getElementById("editTransactionForm");

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

    /* EXPENSE CHART */

    document.querySelectorAll(".bar[data-height]").forEach(function(bar){

        const height = bar.dataset.height;

        if(height){
            bar.style.height = height + "px";
        }

    });

    /* ADD TRANSACTION */

    if(openTransactionBtn){

        openTransactionBtn.addEventListener("click", function(){

            openModal(transactionModal);

        });

    }

    if(closeTransactionBtn){

        closeTransactionBtn.addEventListener("click", function(){

            closeModal(transactionModal);

        });

    }

    /* ADD CARD */

    if(openCardBtn){

        openCardBtn.addEventListener("click", function(){

            openModal(cardModal);

        });

    }

    if(closeCardBtn){

        closeCardBtn.addEventListener("click", function(){

            closeModal(cardModal);

        });

    }

    /* EDIT TRANSACTION */

    openEditTransactionBtns.forEach(function(btn){

        btn.addEventListener("click", function(){

            const id = this.dataset.id;

            if(editTransactionForm){

                editTransactionForm.action =
                    "/transactions/edit/" + id;

            }

            document.getElementById(
                "edit_transaction_title"
            ).value =
                this.dataset.title || "";

            document.getElementById(
                "edit_transaction_amount"
            ).value =
                this.dataset.amount || "";

            document.getElementById(
                "edit_transaction_type"
            ).value =
                this.dataset.type || "expense";

            document.getElementById(
                "edit_transaction_category"
            ).value =
                this.dataset.category || "";

            document.getElementById(
                "edit_transaction_card"
            ).value =
                this.dataset.card || "";

            document.getElementById(
                "edit_transaction_description"
            ).value =
                this.dataset.description || "";

            openModal(editTransactionModal);

        });

    });

    if(closeEditTransactionBtn){

        closeEditTransactionBtn.addEventListener("click", function(){

            closeModal(editTransactionModal);

        });

    }

    /* CLOSE WHEN CLICK OUTSIDE */

    [
        transactionModal,
        editTransactionModal,
        cardModal
    ].forEach(function(modal){

        if(modal){

            modal.addEventListener("click", function(e){

                if(e.target === modal){

                    closeModal(modal);

                }

            });

        }

    });

});