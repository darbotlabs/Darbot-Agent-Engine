(() => {
  const notyf = new Notyf({
    position: { x: "right", y: "top" },
    ripple: false,
    duration: 3000,
  });
  // Always use proxy approach (empty string) for API endpoint
  setStoredData('apiEndpoint', '');
  const apiEndpoint = '';
  
  console.log('Home page loaded, using proxy approach for API calls');
  
  if (typeof window.BACKEND_API_URL !== 'undefined' && window.BACKEND_API_URL !== '') {
    console.log('Warning: BACKEND_API_URL is set but using proxy approach instead');
  }
  
  const newTaskPrompt = document.getElementById("newTaskPrompt");
  const startTaskButton = document.getElementById("startTaskButton");
  const startTaskButtonContainer = document.querySelector(".send-button");
  const startTaskButtonImg = startTaskButtonContainer
    ? startTaskButtonContainer.querySelector("img")
    : null;

  newTaskPrompt.focus();

  // Create spinner element
  const createSpinner = () => {
    if (!document.getElementById("spinnerContainer")) {
      const spinnerContainer = document.createElement("div");
      spinnerContainer.id = "spinnerContainer";
      spinnerContainer.innerHTML = `
       <div id="spinnerLoader">
        <i class="fa-solid fa-circle-notch fa-spin"></i>
        <span class="mt-3"></span>
    </div>
        
      `;
      document.body.appendChild(spinnerContainer);
    }
  };

  // Function to create and add the overlay
  const createOverlay = () => {
    let overlay = document.getElementById("overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "overlay";
      document.body.appendChild(overlay);
    }
  };

  const showOverlay = () => {
    const overlay = document.getElementById("overlay");
    if (overlay) {
      overlay.style.display = "block";
    }
    createSpinner();
  };

  const hideOverlay = () => {
    const overlay = document.getElementById("overlay");
    if (overlay) {
      overlay.style.display = "none";
    }
    removeSpinner();
  };

  // Remove spinner element
  const removeSpinner = () => {
    const spinnerContainer = document.getElementById("spinnerContainer");
    if (spinnerContainer) {
      spinnerContainer.remove();
    }
  };

  // Function to update button image based on textarea content
  const updateButtonImage = () => {
    if (startTaskButtonImg) {
      if (newTaskPrompt.value.trim() === "") {
        startTaskButtonImg.src = "../assets/images/air-button.svg";
        startTaskButton.disabled = true;
      } else {
        startTaskButtonImg.src = "/assets/Send.svg";
        startTaskButtonImg.style.width = "16px";
        startTaskButtonImg.style.height = "16px";
        startTaskButton.disabled = false;
      }
    }
  };

  const startTask = () => {
    startTaskButton.addEventListener("click", (event) => {
      console.log('Start task button clicked');
      if (startTaskButton.disabled) {
        console.log('Button is disabled, returning');
        return;
      }
      const sessionId =
        "sid_" + new Date().getTime() + "_" + Math.floor(Math.random() * 10000);

      console.log('Generated session ID:', sessionId);
      console.log('Task description:', newTaskPrompt.value);

      newTaskPrompt.disabled = true;
      startTaskButton.disabled = true;
      startTaskButton.classList.add("is-loading");      createOverlay();
      showOverlay();      window.headers.then((headers) => {
        // Thought into existence by Darbot
        // Use /api/input_task for Azure task creation
        fetch("/api/input_task", {
          method: "POST",
          headers: headers,
          body: JSON.stringify({
            session_id: sessionId,
            description: newTaskPrompt.value,
          }),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then((data) => {
            console.log('Task creation response:', data);
            if (data.status == "Plan not created" || data.plan_id == "") {
              notyf.error("Unable to create plan for this task.");
              newTaskPrompt.disabled = false;
              startTaskButton.disabled = false;
              startTaskButton.classList.remove("is-loading");
              hideOverlay();
              return;
            }

            newTaskPrompt.disabled = false;
            startTaskButton.disabled = false;
            startTaskButton.classList.remove("is-loading");

            console.log('Sending postMessage to parent window:', {
              action: "taskStarted",
              session_id: data.session_id,
              task_id: data.plan_id,
              task_name: newTaskPrompt.value,
            });

            window.parent.postMessage(
              {
                action: "taskStarted",
                session_id: data.session_id,
                task_id: data.plan_id,
                task_name: newTaskPrompt.value,
              },
              "*"
            );

            newTaskPrompt.value = "";

            // Reset character count to 0
            const charCount = document.getElementById("charCount");
            if (charCount) {
              charCount.textContent = "0";
            }
            updateButtonImage();
            notyf.success("Task created successfully. AI agents are on it!");

            // Remove spinner and hide overlay
            removeSpinner();
            hideOverlay();
          })
          .catch((error) => {
            notyf.error("Error creating task: " + error.message);
            newTaskPrompt.disabled = false;
            startTaskButton.disabled = false;
            startTaskButton.classList.remove("is-loading");
            hideOverlay();
          });
      });
    });
  };

  const quickTasks = () => {
    document.querySelectorAll(".quick-task").forEach((task) => {
      task.addEventListener("click", (event) => {
        const quickTaskPrompt =
          task.querySelector(".quick-task-prompt").innerHTML;
        newTaskPrompt.value = quickTaskPrompt.trim().replace(/\s+/g, " ");
        const charCount = document.getElementById("charCount");
        // Update character count
        charCount.textContent = newTaskPrompt.value.length;
        updateButtonImage();
        newTaskPrompt.focus();
      });
    });
  };
  const handleTextAreaTyping = () => {
    const newTaskPrompt = document.getElementById("newTaskPrompt");
    newTaskPrompt.addEventListener("input", () => {
      // const textInput = document.getElementById("newTaskPrompt");
      const charCount = document.getElementById("charCount");

      // Update character count
      charCount.textContent = newTaskPrompt.value.length;

      // Dynamically adjust height
      newTaskPrompt.style.height = "auto";
      newTaskPrompt.style.height = newTaskPrompt.scrollHeight + "px";

      updateButtonImage();
    });

    newTaskPrompt.addEventListener("keydown", (event) => {
      const textValue = newTaskPrompt.value.trim();
      // If Enter is pressed without Shift, and the textarea is empty, prevent default behavior
      if (event.key === "Enter" && !event.shiftKey) {
        if (textValue === "") {
          event.preventDefault(); // Disable Enter when textarea is empty
        } else {
          // If there's content in the textarea, allow Enter to trigger the task button click
          startTaskButton.click();
        }
      } else if (event.key === "Enter" && event.shiftKey) {
        return;
      }
    });  };

  // Thought into existence by Darbot
  // Theme toggle logic removed - now handled by main app.js

  updateButtonImage();
  startTask();
  quickTasks();
  handleTextAreaTyping();
})();
