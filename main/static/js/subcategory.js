document.addEventListener("DOMContentLoaded", () => {
    const openButtons = document.querySelectorAll('[data-dialog-target="dialog"]'); // Select all buttons that open the modal
    const backdrop = document.querySelector('[data-dialog-backdrop="dialog"]');
    const closeButtons = document.querySelectorAll('[data-dialog-close="true"]');

    if (openButtons && backdrop) {
        // Function to open the modal
        const openModal = () => {
            backdrop.classList.remove("pointer-events-none", "opacity-0");
            backdrop.classList.add("opacity-100");
        };

        // Function to close the modal
        const closeModal = () => {
            backdrop.classList.add("pointer-events-none", "opacity-0");
            backdrop.classList.remove("opacity-100");
        };

        // Add event listeners to all open buttons
        openButtons.forEach((button) => {
            button.addEventListener("click", openModal);
        });

        // Add event listeners to all close buttons
        closeButtons.forEach((button) => {
            button.addEventListener("click", closeModal);
        });

        // Close the modal when the backdrop is clicked
        backdrop.addEventListener("click", (event) => {
            if (event.target === backdrop && backdrop.dataset.dialogBackdropClose === "true") {
                closeModal();
            }
        });
    }
});