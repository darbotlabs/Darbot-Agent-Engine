(() => {
    window.headers = GetAuthDetails();
    // Always use proxy approach (empty string) for API calls
    const apiEndpoint = '';
    setStoredData('apiEndpoint', '');
    console.log('App initialized, using proxy approach for API calls');
    const goHomeButton = document.getElementById("goHomeButton");
    const newTaskButton = document.getElementById("newTaskButton");
    const closeModalButtons = document.querySelectorAll(".modal-close-button");
    const myTasksMenu = document.getElementById("myTasksMenu");
    const tasksStats = document.getElementById("tasksStats");
    const taskAgentsModal = document.getElementById("taskAgentsModal");
    const taskWokFlowModal = document.getElementById("taskWokFlowModal");
      // Thought into existence by Darbot - Safe AUTH_ENABLED check
    if(typeof AUTH_ENABLED !== 'undefined') {
        setStoredData('authEnabled', AUTH_ENABLED.toString().toLowerCase());
    } else {
        // Default to false for local development
        setStoredData('authEnabled', 'false');
        console.log('AUTH_ENABLED not defined, defaulting to false for local development');
    }

    //if (!getStoredData('apiEndpoint'))setStoredData('apiEndpoint', apiEndpoint);
    // Force rewrite of apiEndpoint   setStoredData('apiEndpoint', '');  // Always use empty for proxy approach
   setStoredData('context', 'employee');
    // Refresh rate is set
    if (!getStoredData('apiRefreshRate'))setStoredData('apiRefreshRate', 5000);
    if (!getStoredData('actionStagesRun'))setStoredData('actionStagesRun', []);

    const getQueryParam = (param) => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    };

    const setQueryParam = (param, value) => {
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set(param, value);
        window.history.replaceState(null, null, `?${urlParams.toString()}`);
    };

    const switchView = () => {
        const viewIframe = document.getElementById('viewIframe');
        if (viewIframe) {
            const viewRoute = getQueryParam('v');
            const viewContext = getStoredData('context');
            const noCache = '?nocache=' + new Date().getTime();
            console.log(`Switching view to: ${viewRoute || 'default'}`);
            switch (viewRoute) {
                case 'home':
                    viewIframe.src = 'home/home.html' + noCache;
                    break;
                case 'task':
                    viewIframe.src = `task/${viewContext}.html` + noCache;
                    break;
                default:
                    viewIframe.src = 'home/home.html' + noCache;
            }
            console.log(`Iframe src set to: ${viewIframe.src}`);
        } else {
            console.error('viewIframe element not found');
        }
    };
    // get user session 
    const getUserInfo = async () => {
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Runninng in Azure so get user info from /.auth/me
          try {
              const response = await fetch('/.auth/me');
              if (!response.ok) {
                  if(getStoredData('authEnabled') === 'false'){
                        //Authentication is disabled. Will use mock user
                        return {
                            name: 'Local User',
                            authenticated: true
                        }
                  }
                  else{
                    console.log("No identity provider found. Access to chat will be blocked.");
                    return null;
                  }
              }
              const payload = await response.json();

              if (payload) {
                  return payload;
              }
              return null;
            } catch (e) {
                console.error("Error fetching user info:", e);
                return null;
            }
        } else {
            // Running locally so use a mock user
            return {
                name: 'Local User',
                authenticated: true
            }
        }
    };

    const homeActions = () => {
        if (newTaskButton && goHomeButton) {
            newTaskButton.addEventListener('click', (event) => {
                event.preventDefault();
                setQueryParam('v', 'home');
                switchView();
            });
    
            goHomeButton.addEventListener('click', (event) => {
                event.preventDefault();
                setQueryParam('v', 'home');
                switchView();
            });
        }
    };

    const messageListeners = () => {

        window.addEventListener('message', (event) => {
            console.log('Received message:', event.data);
            if (event.data && event.data.button) {
                if (event.data.button === 'taskAgentsButton') taskAgentsModal.classList.add('is-active');
                if (event.data.button === 'taskWokFlowButton') taskWokFlowModal.classList.add('is-active');
            }
            if (event.data && event.data.action) {
                if (event.data.action === 'taskStarted') {
                    console.log('Task started event received, fetching tasks...');
                    fetchTasksIfNeeded();
                }
            }
        });

    }

    const getMyTasks = () => {
        myTasksMenu.innerHTML = `
            <div class="notification">
                <i class="fa-solid fa-circle-notch fa-spin mr-3"></i> Loading tasks...
            </div>
        `;
    }

    // Thought into existence by Darbot
    // Use correct Azure endpoints for task creation and plan fetch
    const createTask = async (sessionId, description, headers) => {
      return fetch("/api/input_task", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          session_id: sessionId,
          description: description,
        }),
      }).then((response) => response.json());
    };

    const fetchPlans = async (session_id, headers) => {
      return fetch(`/api/plans?session_id=${session_id}`, {
        method: "GET",
        headers: headers,
      }).then((response) => response.json());
    };

    const fetchTasksIfNeeded = async () => {
        console.log('fetchTasksIfNeeded called');
        const taskStoreData = getStoredData('task');
        const taskStore = taskStoreData ? JSON.parse(taskStoreData) : null;
        console.log('API endpoint for plans:', '/api/plans (proxied through frontend)');
        window.headers
            .then(headers => {
                console.log('Headers resolved, making fetch request');
                fetch('/api/plans', {  // Using relative URL for the proxy
                    method: 'GET',
                    headers: headers,
                })
                    .then(response => {
                        console.log('Fetch response received:', response.status, response.statusText);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Fetched plans data:', data);
        
                        if (myTasksMenu){
                            myTasksMenu.innerHTML = '';
                        }
        
                        if (data && Array.isArray(data) && data.length > 0) {
        
                            const lastFiveTasks = data.slice(-5);
                            let taskCount = 1;
                            let inProgressTaskCount = 0;
                            let inCompletedTaskCount = 0;
                            let stagesPlannedCount = 0;
                            let stagesRejectedCount = 0;
        
                            lastFiveTasks.forEach(task => {
                                if (!task || !task.session_id || !task.initial_goal) {
                                    console.warn('Invalid task data:', task);
                                    return;
                                }
                                
                                const newTaskItem = document.createElement('li');
                                const completedSteps = task.completed || 0;
                                const totalSteps = task.total_steps || 0;
                                let taskActive = '';
        
                                if (taskStore && taskStore.id === task.session_id) taskActive = 'is-active';
        
                                const taskStatus = (task.overall_status === 'completed') ? '<i class="fa-solid fa-check-to-slot has-text-success mr-3"></i>' : '<i class="fa-solid fa-arrows-rotate fa-spin mr-3"></i>';
        
                                newTaskItem.innerHTML = `
                                <a href class="menu-task ${taskActive}" data-name="${task.initial_goal}" data-id="${task.session_id}" title="Status: ${task.overall_status}, Session id: ${task.session_id} ">
                                    ${taskStatus}
                                    <span>${taskCount}.  ${task.initial_goal}</span>
                                    <div class="tag is-dark ml-3">${completedSteps}/${totalSteps}</div>
                                </a>
                                `;
                                
                                if(myTasksMenu){
                                    myTasksMenu.appendChild(newTaskItem);
                                }
        
                                newTaskItem.querySelector('.menu-task').addEventListener('click', (event) => {
                                    const sessionId = event.target.closest('.menu-task').dataset.id;
                                    const taskName = event.target.closest('.menu-task').dataset.name;
        
                                    event.preventDefault();
                                    setQueryParam('v', 'task');
                                    switchView();
        
                                   setStoredData('task', JSON.stringify({
                                        id: sessionId,
                                        name: taskName
                                    }));
        
                                    document.querySelectorAll('.menu-task').forEach(task => {
                                        task.classList.remove('is-active');
                                    });
        
                                    event.target.closest('.menu-task').classList.add('is-active');
                                });
        
                                if (task.overall_status === 'completed') inCompletedTaskCount++;
                                if (task.overall_status !== 'completed') inProgressTaskCount++;
                                if (task.overall_status === 'planned') stagesPlannedCount++;
                                if (task.overall_status === 'rejected') stagesRejectedCount++;
        
                                const addS = (word, count) => (count === 1) ? word : word + 's';
                                
                                if(tasksStats){
                                    tasksStats.innerHTML = `
                                        <li><a><strong>${inCompletedTaskCount}</strong> ${addS('task', inCompletedTaskCount)} completed</a></li>
                                        <li><a><strong>${inProgressTaskCount}</strong> ${addS('task', inProgressTaskCount)} in progress</a></li>
                                    `;
                                }
        
                                taskCount++;
        
                            })
                        } else {
                            // No tasks found
                            if(myTasksMenu) {
                                myTasksMenu.innerHTML = '<li><div class="notification is-info">No tasks found. Create your first task!</div></li>';
                            }
                            if(tasksStats) {
                                tasksStats.innerHTML = '<li><a><strong>0</strong> tasks</a></li>';
                            }
                        }
        
                    })
                    .catch(error => {
                        console.error('Error fetching tasks:', error);
                        if(myTasksMenu) {
                            myTasksMenu.innerHTML = '<div class="notification is-danger">Error loading tasks</div>';
                        }
                    })

    })
       
    };

    const modalActions = () => {
        closeModalButtons.forEach(closeModalButton => {
            closeModalButton.addEventListener('click', (event) => {
                event.preventDefault();
                const modal = closeModalButton.closest('.modal');
                modal.classList.remove('is-active');
            });
        });
    };

    const themeActions = () => {
        const themeToggle = document.getElementById("themeToggle");
        const html = document.documentElement;
        
        // Initialize theme from localStorage or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        updateThemeToggle(savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', (event) => {
                event.preventDefault();
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateThemeToggle(newTheme);
            });
        }
    };
    
    const updateThemeToggle = (theme) => {
        const themeToggle = document.getElementById("themeToggle");
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            const text = themeToggle.querySelector('span');
            
            if (theme === 'dark') {
                icon.className = 'fa-solid fa-sun mr-2';
                text.textContent = 'Light Mode';
            } else {
                icon.className = 'fa-solid fa-moon mr-2';
                text.textContent = 'Dark Mode';
            }
        }
    };

    const initializeApp = async () => {
        // Fetch user info when the app loads
        const userInfo = await getUserInfo();
        if (!userInfo) {
            console.error("Authentication failed. Access to tasks is restricted.");
        } else {
           setStoredData('userInfo', userInfo);
            await fetchTasksIfNeeded();  // Fetch tasks after initialization if needed
        }
    };

    fetchTasksIfNeeded();
    initializeApp();
    homeActions();
    switchView();
    messageListeners();
    modalActions();
    themeActions();
})();
