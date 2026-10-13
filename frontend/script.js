const state = {
    selectedFile: null,
    answerText: "",
    agentText: "",
    matchFile: null,
    token: sessionStorage.getItem("ai_jd_access_token") || "",
};

const els = {};

function cacheEls() {
    els.authPanel = document.getElementById("authPanel");
    els.authEmail = document.getElementById("authEmail");
    els.authPassword = document.getElementById("authPassword");
    els.loginBtn = document.getElementById("loginBtn");
    els.registerBtn = document.getElementById("registerBtn");
    els.logoutBtn = document.getElementById("logoutBtn");
    els.currentPassword = document.getElementById("currentPassword");
    els.newPassword = document.getElementById("newPassword");
    els.confirmPassword = document.getElementById("confirmPassword");
    els.changePasswordBtn = document.getElementById("changePasswordBtn");
    els.authResult = document.getElementById("authResult");
    els.fileInput = document.getElementById("fileInput");
    els.dropzone = document.getElementById("dropzone");
    els.fileMeta = document.getElementById("fileMeta");
    els.uploadResult = document.getElementById("uploadResult");
    els.uploadBtn = document.getElementById("uploadBtn");
    els.clearFileBtn = document.getElementById("clearFileBtn");
    els.refreshDocsBtn = document.getElementById("refreshDocsBtn");
    els.questionInput = document.getElementById("questionInput");
    els.topKSelect = document.getElementById("topKSelect");
    els.askBtn = document.getElementById("askBtn");
    els.clearQuestionBtn = document.getElementById("clearQuestionBtn");
    els.answerBox = document.getElementById("answerBox");
    els.copyAnswerBtn = document.getElementById("copyAnswerBtn");
    els.sourceList = document.getElementById("sourceList");
    els.taskInput = document.getElementById("taskInput");
    els.agentBtn = document.getElementById("agentBtn");
    els.clearTaskBtn = document.getElementById("clearTaskBtn");
    els.agentResult = document.getElementById("agentResult");
    els.matchResumeInput = document.getElementById("matchResumeInput");
    els.matchResumeLabel = document.getElementById("matchResumeLabel");
    els.matchJdInput = document.getElementById("matchJdInput");
    els.matchBtn = document.getElementById("matchBtn");
    els.matchAsyncBtn = document.getElementById("matchAsyncBtn");
    els.matchStatus = document.getElementById("matchStatus");
    els.matchResult = document.getElementById("matchResult");
    els.copyAgentBtn = document.getElementById("copyAgentBtn");
    els.documentList = document.getElementById("documentList");
    els.historyList = document.getElementById("historyList");
    els.refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
    els.docCount = document.getElementById("docCount");
    els.historyCount = document.getElementById("historyCount");
    els.appStatus = document.getElementById("appStatus");
}

function setStatus(text) {
    els.appStatus.textContent = text;
}

function setButtonLoading(button, loading, text) {
    if (!button) return;
    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = text || "处理中...";
        button.classList.add("loading");
        button.disabled = true;
    } else {
        button.textContent = button.dataset.originalText || button.textContent;
        button.classList.remove("loading");
        button.disabled = false;
    }
}

function showEmpty(element, text) {
    element.textContent = text;
    element.classList.add("empty");
}

function clearEmpty(element) {
    element.classList.remove("empty");
}

function fileLabel(file) {
    if (!file) return "未选择文件";
    const sizeKb = (file.size / 1024).toFixed(1);
    return `${file.name} · ${sizeKb} KB`;
}

function renderDocuments(items) {
    els.documentList.innerHTML = "";

    if (!items.length) {
        const li = document.createElement("li");
        li.textContent = "暂无文档";
        els.documentList.appendChild(li);
        els.docCount.textContent = "0";
        return;
    }

    els.docCount.textContent = String(items.length);

    items.forEach((item) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <span class="list-title">${escapeHtml(item.filename || "未命名文件")}</span>
            <span>${item.chunk_count ?? 0} 个片段</span>
            <span class="list-meta">${item.created_at || ""}</span>
        `;
        els.documentList.appendChild(li);
    });
}

function renderHistory(items) {
    els.historyList.innerHTML = "";

    if (!items.length) {
        const li = document.createElement("li");
        li.textContent = "暂无历史记录";
        els.historyList.appendChild(li);
        els.historyCount.textContent = "0";
        return;
    }

    els.historyCount.textContent = String(items.length);

    items.forEach((item) => {
        const li = document.createElement("li");
        const preview = (item.answer || "").slice(0, 70);
        li.innerHTML = `
            <span class="list-title">${escapeHtml(item.question || "无标题问题")}</span>
            <span>${escapeHtml(preview)}${item.answer && item.answer.length > 70 ? "..." : ""}</span>
            <span class="list-meta">${item.created_at || ""}</span>
        `;
        els.historyList.appendChild(li);
    });
}

function renderSources(sources) {
    els.sourceList.innerHTML = "";

    if (!sources || !sources.length) {
        const li = document.createElement("li");
        li.textContent = "暂无来源";
        els.sourceList.appendChild(li);
        return;
    }

    sources.forEach((source, index) => {
        const li = document.createElement("li");
        const meta = [source.filename, `片段 ${source.chunk_index ?? index}`].filter(Boolean).join(" / ");
        li.innerHTML = `
            <span class="list-title">${escapeHtml(meta)}</span>
            <span>${escapeHtml(source.content || "")}</span>
            <span class="badge">distance ${formatDistance(source.distance)}</span>
        `;
        els.sourceList.appendChild(li);
    });
}

function renderMatch(result) {
    const list = (items) => (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>None identified</li>";
    els.matchResult.innerHTML = `
        <div class="match-score"><strong>${Number(result.match_score || 0).toFixed(1)}</strong><span>/ 100</span></div>
        <p class="match-summary">${escapeHtml(result.summary || "")}</p>
        <div class="match-columns">
            <div><h4>Matching skills</h4><ul>${list(result.matching_skills)}</ul></div>
            <div><h4>Missing skills</h4><ul>${list(result.missing_skills)}</ul></div>
            <div><h4>Strengths</h4><ul>${list(result.strengths)}</ul></div>
            <div><h4>Gaps</h4><ul>${list(result.gaps)}</ul></div>
            <div><h4>Recommendations</h4><ul>${list(result.recommendations)}</ul></div>
        </div>`;
    clearEmpty(els.matchResult);
}

function matchForm() {
    const form = new FormData();
    form.append("resume", state.matchFile);
    form.append("job_description", els.matchJdInput.value.trim());
    return form;
}

async function matchResume(asyncMode = false) {
    if (!state.matchFile) {
        els.matchStatus.textContent = "Choose a resume first";
        return;
    }
    if (!els.matchJdInput.value.trim()) {
        els.matchStatus.textContent = "Paste a job description first";
        return;
    }
    const button = asyncMode ? els.matchAsyncBtn : els.matchBtn;
    setButtonLoading(button, true, asyncMode ? "Submitting..." : "Matching...");
    els.matchStatus.textContent = asyncMode ? "Queued" : "Running";
    try {
        const payload = await requestJson(`/match-resume-jd${asyncMode ? "/async" : ""}`, { method: "POST", body: matchForm() });
        if (!asyncMode) {
            renderMatch(payload.data);
            els.matchStatus.textContent = "Complete";
            return;
        }
        const taskId = payload.data.task_id;
        for (let attempt = 0; attempt < 60; attempt += 1) {
            await new Promise((resolve) => setTimeout(resolve, 1000));
            const task = await requestJson(`/tasks/${taskId}`);
            if (task.data.status === "succeeded") {
                renderMatch(task.data.result);
                els.matchStatus.textContent = "Complete";
                return;
            }
            if (task.data.status === "failed") throw new Error(task.data.error || "Match task failed");
            els.matchStatus.textContent = `Running (${task.data.status})`;
        }
        throw new Error("Task timed out");
    } catch (error) {
        els.matchStatus.textContent = error.message;
        showEmpty(els.matchResult, "Unable to complete match");
    } finally {
        setButtonLoading(button, false);
    }
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function formatDistance(value) {
    if (value === undefined || value === null || Number.isNaN(Number(value))) {
        return "-";
    }
    return Number(value).toFixed(3);
}

async function requestJson(url, options) {
    const requestOptions = { ...(options || {}), headers: { ...((options || {}).headers || {}) } };
    const requestToken = state.token;
    const isAuth = url === "/auth/login" || url === "/auth/register";
    if (requestToken && !isAuth) requestOptions.headers.Authorization = `Bearer ${requestToken}`;
    const response = await fetch(url, requestOptions);
    const payload = await response.json().catch(() => ({}));

    if (!isAuth && requestToken !== state.token) throw new Error("Session changed");
    if (response.status === 401 && !isAuth) setAuthenticated("");

    if (!response.ok) {
        throw new Error(payload.detail || payload.message || `请求失败：${response.status}`);
    }

    return payload;
}

function setAuthenticated(token) {
    state.token = token || "";
    localStorage.removeItem("ai_jd_access_token");
    if (state.token) sessionStorage.setItem("ai_jd_access_token", state.token);
    else sessionStorage.removeItem("ai_jd_access_token");
    els.authPanel.hidden = false;
    [els.authEmail, els.authPassword, els.loginBtn, els.registerBtn].forEach(el => { el.hidden = Boolean(state.token); });
    els.logoutBtn.hidden = !state.token;
    [els.currentPassword, els.newPassword, els.confirmPassword, els.changePasswordBtn].forEach(el => { el.hidden = !state.token; });
    document.querySelector("main.app-shell").hidden = !state.token;
    els.authPassword.value = "";
    state.answerText = "";
    state.agentText = "";
    state.selectedFile = null;
    els.fileInput.value = "";
    els.fileMeta.textContent = "";
    els.uploadResult.textContent = "";
    els.questionInput.value = "";
    els.taskInput.value = "";
    els.answerBox.textContent = "";
    els.agentResult.textContent = "";
    renderDocuments([]);
    renderHistory([]);
    renderSources([]);
    els.authResult.textContent = state.token ? "登录成功" : "请先登录";
}

async function authenticate(mode) {
    const email = els.authEmail.value.trim();
    const password = els.authPassword.value;
    if (!email || !password) {
        els.authResult.textContent = "请输入邮箱和密码";
        return;
    }
    try {
        const options = mode === "login"
            ? { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ username: email, password }) }
            : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) };
        const payload = await requestJson(`/auth/${mode}`, options);
        setAuthenticated(payload.access_token || payload.data.access_token);
        els.authResult.textContent = "认证成功";
        await Promise.all([loadDocuments(), loadHistory()]);
    } catch (error) {
        els.authResult.textContent = error.message;
    }
}

async function loadDocuments() {
    const payload = await requestJson("/rag/documents");
    renderDocuments(payload.data || []);
}

async function loadHistory() {
    const payload = await requestJson("/rag/history");
    renderHistory(payload.data || []);
}

async function uploadDocument() {
    if (!state.selectedFile) {
        els.uploadResult.textContent = "请先选择文件";
        return;
    }

    const formData = new FormData();
    formData.append("file", state.selectedFile);

    setButtonLoading(els.uploadBtn, true, "上传中...");
    setStatus("Uploading");
    els.uploadResult.textContent = "正在上传并入库...";

    try {
        const payload = await requestJson("/rag/documents/upload", {
            method: "POST",
            body: formData,
        });

        els.uploadResult.textContent = `上传成功：${payload.data.filename}，${payload.data.chunk_count} 个片段`;
        await Promise.all([loadDocuments(), loadHistory()]);
        setStatus("Idle");
    } catch (error) {
        els.uploadResult.textContent = `上传失败：${error.message}`;
        setStatus("Error");
    } finally {
        setButtonLoading(els.uploadBtn, false);
    }
}

async function askQuestion() {
    const question = els.questionInput.value.trim();
    if (!question) {
        showEmpty(els.answerBox, "请输入问题");
        return;
    }

    const top_k = Number(els.topKSelect.value || 3);
    setButtonLoading(els.askBtn, true, "思考中...");
    setStatus("RAG Query");
    showEmpty(els.answerBox, "正在检索和生成答案...");

    try {
        const payload = await requestJson("/rag/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question, top_k }),
        });

        state.answerText = payload.data.answer || "";
        els.answerBox.textContent = state.answerText || "无返回内容";
        clearEmpty(els.answerBox);
        renderSources(payload.data.sources || []);
        await loadHistory();
        setStatus("Idle");
    } catch (error) {
        els.answerBox.textContent = `问答失败：${error.message}`;
        clearEmpty(els.answerBox);
        setStatus("Error");
    } finally {
        setButtonLoading(els.askBtn, false);
    }
}

async function runAgent() {
    const task = els.taskInput.value.trim();
    if (!task) {
        showEmpty(els.agentResult, "请输入任务");
        return;
    }

    setButtonLoading(els.agentBtn, true, "执行中...");
    setStatus("Agent Running");
    showEmpty(els.agentResult, "Agent 正在编排工具...");

    try {
        const payload = await requestJson("/agent/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ task }),
        });

        const data = payload.data || {};
        const output = data.markdown_report || data.final_answer || JSON.stringify(data, null, 2);
        state.agentText = output;
        els.agentResult.textContent = output;
        clearEmpty(els.agentResult);
        setStatus("Idle");
    } catch (error) {
        els.agentResult.textContent = `Agent 运行失败：${error.message}`;
        clearEmpty(els.agentResult);
        setStatus("Error");
    } finally {
        setButtonLoading(els.agentBtn, false);
    }
}

async function copyText(text) {
    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
    } catch {
        const temp = document.createElement("textarea");
        temp.value = text;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand("copy");
        temp.remove();
    }
}

async function authenticate(mode) {
    const email = els.authEmail.value.trim();
    const password = els.authPassword.value;
    if (!email || !password) {
        els.authResult.textContent = "请输入邮箱和密码";
        return;
    }
    try {
        const options = mode === "login"
            ? { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ username: email, password }) }
            : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) };
        const payload = await requestJson(`/auth/${mode}`, options);
        setAuthenticated(payload.access_token || payload.data.access_token);
        els.authResult.textContent = mode === "login" ? "登录成功" : "注册成功，已自动登录";
        await Promise.all([loadDocuments(), loadHistory()]);
    } catch (error) {
        els.authResult.textContent = error.message || "操作失败，请稍后重试";
    }
}

async function changePassword() {
    const currentPassword = els.currentPassword.value;
    const newPassword = els.newPassword.value;
    const confirmPassword = els.confirmPassword.value;
    if (!currentPassword || !newPassword || !confirmPassword) {
        els.authResult.textContent = "请完整填写密码信息";
        return;
    }
    if (newPassword !== confirmPassword) {
        els.authResult.textContent = "两次输入的新密码不一致";
        return;
    }
    try {
        await requestJson("/auth/password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }) });
        els.currentPassword.value = "";
        els.newPassword.value = "";
        els.confirmPassword.value = "";
        els.authResult.textContent = "密码修改成功，请使用新密码登录";
    } catch (error) {
        els.authResult.textContent = error.message || "密码修改失败，请稍后重试";
    }
}

function bindEvents() {
    els.loginBtn.addEventListener("click", () => authenticate("login"));
    els.registerBtn.addEventListener("click", () => authenticate("register"));
    els.logoutBtn.addEventListener("click", () => setAuthenticated(""));
    els.changePasswordBtn.addEventListener("click", changePassword);
    els.fileInput.addEventListener("change", () => {
        state.selectedFile = els.fileInput.files[0] || null;
        els.fileMeta.textContent = fileLabel(state.selectedFile);
        els.uploadResult.textContent = state.selectedFile ? "已选择文件，等待上传" : "未选择文件";
    });

    els.dropzone.addEventListener("dragover", (event) => {
        event.preventDefault();
        els.dropzone.classList.add("drag-over");
    });

    els.dropzone.addEventListener("dragleave", () => {
        els.dropzone.classList.remove("drag-over");
    });

    els.dropzone.addEventListener("drop", (event) => {
        event.preventDefault();
        els.dropzone.classList.remove("drag-over");
        const file = event.dataTransfer.files[0];
        if (!file) return;
        state.selectedFile = file;
        const transfer = new DataTransfer();
        transfer.items.add(file);
        els.fileInput.files = transfer.files;
        els.fileMeta.textContent = fileLabel(file);
        els.uploadResult.textContent = "已拖入文件，等待上传";
    });

    els.uploadBtn.addEventListener("click", uploadDocument);
    els.clearFileBtn.addEventListener("click", () => {
        state.selectedFile = null;
        els.fileInput.value = "";
        els.fileMeta.textContent = "未选择文件";
        els.uploadResult.textContent = "等待上传";
    });
    els.refreshDocsBtn.addEventListener("click", loadDocuments);
    els.askBtn.addEventListener("click", askQuestion);
    els.clearQuestionBtn.addEventListener("click", () => {
        els.questionInput.value = "";
        showEmpty(els.answerBox, "等待提问");
        els.sourceList.innerHTML = "";
    });
    els.copyAnswerBtn.addEventListener("click", () => copyText(state.answerText));
    els.agentBtn.addEventListener("click", runAgent);
    els.clearTaskBtn.addEventListener("click", () => {
        els.taskInput.value = "";
        showEmpty(els.agentResult, "等待执行");
        state.agentText = "";
    });
    els.copyAgentBtn.addEventListener("click", () => copyText(state.agentText));
    els.refreshHistoryBtn.addEventListener("click", loadHistory);
    els.matchResumeInput.addEventListener("change", () => {
        state.matchFile = els.matchResumeInput.files[0] || null;
        els.matchResumeLabel.textContent = state.matchFile ? state.matchFile.name : "Choose resume";
    });
    els.matchBtn.addEventListener("click", () => matchResume(false));
    els.matchAsyncBtn.addEventListener("click", () => matchResume(true));
}

async function boot() {
    cacheEls();
    bindEvents();
    setAuthenticated(state.token);
    showEmpty(els.answerBox, "等待提问");
    showEmpty(els.agentResult, "等待执行");
    setStatus("Booting");

    try {
        if (!state.token) {
            setStatus("需要登录");
            return;
        }
        await requestJson("/auth/me");
        await Promise.all([loadDocuments(), loadHistory()]);
        setStatus("Idle");
    } catch (error) {
        setStatus("Offline");
        els.uploadResult.textContent = `初始化失败：${error.message}`;
    }
}

boot();
