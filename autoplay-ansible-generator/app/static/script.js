document.addEventListener('DOMContentLoaded', () => {
    let taskCount = 0;
    let generatedPlaybookId = null;

    const taskTypeSelector = document.getElementById('task-type-selector');
    const addTaskBtn = document.getElementById('add-task-btn');
    const tasksContainer = document.getElementById('tasks-container');
    const noTasksPlaceholder = document.getElementById('no-tasks-placeholder');
    const taskCounter = document.getElementById('task-counter');
    const generatePlaybookBtn = document.getElementById('generate-playbook-btn');

    // Preview and Action panel elements
    const previewPlaceholder = document.getElementById('preview-placeholder');
    const previewResultContainer = document.getElementById('preview-result-container');
    const previewToggleGroup = document.getElementById('preview-toggle-group');
    const yamlCodeBox = document.getElementById('yaml-code-box');
    const iniCodeBox = document.getElementById('ini-code-box');
    const dlPlaybookLink = document.getElementById('dl-playbook-link');
    const dlInventoryLink = document.getElementById('dl-inventory-link');
    const risksContainerList = document.getElementById('risks-container-list');
    const btnShowYaml = document.getElementById('btn-show-yaml');
    const btnShowIni = document.getElementById('btn-show-ini');
    const yamlCodeView = document.getElementById('yaml-code-view');
    const iniCodeView = document.getElementById('ini-code-view');

    // Run inputs
    const privateKeyInput = document.getElementById('private-key-input');
    const dryRunSwitch = document.getElementById('dry-run-switch');
    const runPlaybookBtn = document.getElementById('run-playbook-btn');

    // Map task type to friendly name and icon
    const taskDetails = {
        'install_nginx': { title: 'Install and Configure Nginx', icon: 'bi-globe' },
        'install_docker': { title: 'Install and Start Docker Engine', icon: 'bi-ubuntu' },
        'create_user': { title: 'Create Linux System User', icon: 'bi-person-add' },
        'deploy_container': { title: 'Deploy Docker Container', icon: 'bi-box-seam' },
        'firewall': { title: 'Configure Firewall (Open Port)', icon: 'bi-shield-lock' },
        'custom_command': { title: 'Execute Custom Bash/Shell Script', icon: 'bi-terminal' }
    };

    // Toggle Preview Tabs
    if (btnShowYaml && btnShowIni) {
        btnShowYaml.addEventListener('click', () => {
            btnShowYaml.classList.add('active');
            btnShowIni.classList.remove('active');
            yamlCodeView.style.display = 'block';
            iniCodeView.style.display = 'none';
        });

        btnShowIni.addEventListener('click', () => {
            btnShowIni.classList.add('active');
            btnShowYaml.classList.remove('active');
            yamlCodeView.style.display = 'none';
            iniCodeView.style.display = 'block';
        });
    }

    // Add Task to the builder list
    addTaskBtn.addEventListener('click', () => {
        const selectedType = taskTypeSelector.value;
        if (!selectedType) {
            alert('Please select a task template to add.');
            return;
        }

        // Get template definition from DOM
        const formDef = document.querySelector(`.task-form-def[data-type="${selectedType}"]`);
        if (!formDef) return;

        // Hide placeholder if it's the first task
        if (taskCount === 0) {
            noTasksPlaceholder.style.display = 'none';
        }

        taskCount++;
        updateTaskCounter();

        // Create Task Card element
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.dataset.taskType = selectedType;
        taskCard.dataset.taskId = taskCount;

        const info = taskDetails[selectedType];
        
        // Setup card inner structure
        taskCard.innerHTML = `
            <div class="task-card-header">
                <span class="task-card-title text-info">
                    <i class="bi ${info.icon} me-2"></i> ${info.title}
                </span>
                <span class="task-remove-btn" title="Remove Task">
                    <i class="bi bi-trash fs-5"></i>
                </span>
            </div>
            <div class="task-card-body mt-2">
                ${formDef.innerHTML}
            </div>
        `;

        // Add remove handler
        taskCard.querySelector('.task-remove-btn').addEventListener('click', () => {
            taskCard.remove();
            taskCount--;
            updateTaskCounter();
            if (taskCount === 0) {
                noTasksPlaceholder.style.display = 'block';
            }
        });

        tasksContainer.appendChild(taskCard);
        
        // Reset selector
        taskTypeSelector.value = '';
    });

    function updateTaskCounter() {
        taskCounter.textContent = `${taskCount} Task${taskCount !== 1 ? 's' : ''}`;
    }

    // Generate Playbook
    generatePlaybookBtn.addEventListener('click', async () => {
        if (taskCount === 0) {
            alert('Please add at least one task before compiling.');
            return;
        }

        // Collect metadata
        const name = document.getElementById('playbook-name').value;
        const targetHosts = document.getElementById('target-hosts').value;
        const becomePrivilege = document.getElementById('become-privilege').value;
        const ip = document.getElementById('server-ip').value;
        const user = document.getElementById('ssh-user').value;

        // Collect configured tasks
        const tasks = [];
        const taskCards = tasksContainer.querySelectorAll('.task-card');
        
        taskCards.forEach(card => {
            const taskType = card.dataset.taskType;
            const taskData = { type: taskType };
            
            // Gather all input/select/textarea inputs inside this card
            const fields = card.querySelectorAll('input, select, textarea');
            fields.forEach(field => {
                if (field.name) {
                    taskData[field.name] = field.value;
                }
            });
            tasks.push(taskData);
        });

        const payload = {
            name,
            target_hosts: targetHosts,
            become_privilege: becomePrivilege,
            ip,
            user,
            tasks
        };

        generatePlaybookBtn.disabled = true;
        generatePlaybookBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Compiling...';

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            if (result.success) {
                generatedPlaybookId = result.playbook_id;
                
                // Show result containers
                previewPlaceholder.style.display = 'none';
                previewResultContainer.style.display = 'flex';
                previewToggleGroup.style.display = 'inline-flex';

                // Set code contents
                yamlCodeBox.textContent = result.playbook_yaml;
                iniCodeBox.textContent = result.inventory_ini;

                // Configure download links
                dlPlaybookLink.href = `/playbook/${result.playbook_id}/download-playbook`;
                dlInventoryLink.href = `/playbook/${result.playbook_id}/download-inventory`;

                // Set security risks
                risksContainerList.innerHTML = '';
                if (result.risks && result.risks.length > 0) {
                    result.risks.forEach(risk => {
                        const riskClass = risk.risk.toLowerCase() === 'high' ? 'risk-high' : 
                                          (risk.risk.toLowerCase() === 'medium' ? 'risk-medium' : 'risk-low');
                        
                        const riskEl = document.createElement('div');
                        riskEl.className = `risk-item ${riskClass}`;
                        riskEl.innerHTML = `
                            <strong>[${risk.risk} Risk] ${risk.task}</strong>: ${risk.reason}
                            <div class="mt-1 small text-white-50">💡 Suggestion: ${risk.suggestion}</div>
                        `;
                        risksContainerList.appendChild(riskEl);
                    });
                } else {
                    risksContainerList.innerHTML = `
                        <div class="text-success small p-2">
                            <i class="bi bi-shield-check me-1"></i> No immediate security risks detected in configuration.
                        </div>
                    `;
                }
                
                // Scroll preview into view on mobile
                if (window.innerWidth < 992) {
                    document.getElementById('preview-section').scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                alert(`Error generating playbook: ${result.error}`);
            }
        } catch (err) {
            console.error(err);
            alert('An unexpected network error occurred while generating the playbook.');
        } finally {
            generatePlaybookBtn.disabled = false;
            generatePlaybookBtn.innerHTML = '<i class="bi bi-magic me-1"></i> Compile & Generate Playbook';
        }
    });

    // Run Playbook
    runPlaybookBtn.addEventListener('click', async () => {
        if (!generatedPlaybookId) {
            alert('Please generate the playbook first.');
            return;
        }

        const ip = document.getElementById('server-ip').value || 'localhost';
        const privateKey = privateKeyInput.value;
        const isDryRun = dryRunSwitch.checked;

        if (ip !== 'localhost' && !privateKey && !confirm('No SSH private key specified. Continue anyway? (Assumes local daemon or agent access)')) {
            return;
        }

        runPlaybookBtn.disabled = true;
        runPlaybookBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Spawning Runner...';

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    playbook_id: generatedPlaybookId,
                    ip: ip,
                    private_key: privateKey,
                    is_dry_run: isDryRun
                })
            });

            const result = await response.json();
            if (result.success) {
                // Redirect to console run screen
                window.location.href = `/console/${result.run_id}`;
            } else {
                alert(`Error starting execution: ${result.error}`);
                runPlaybookBtn.disabled = false;
                runPlaybookBtn.innerHTML = '<i class="bi bi-play-fill"></i> Trigger Remote Deployment';
            }
        } catch (err) {
            console.error(err);
            alert('Network failure occurred while launching the execution runner.');
            runPlaybookBtn.disabled = false;
            runPlaybookBtn.innerHTML = '<i class="bi bi-play-fill"></i> Trigger Remote Deployment';
        }
    });
});

// Clipboard Helper
function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        const copyBtn = document.querySelector(`#${elementId}`).parentElement.parentElement.querySelector('.copy-btn');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}
