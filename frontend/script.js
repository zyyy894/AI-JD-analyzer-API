async function runAgent() {
    const task = document.getElementById("taskInput").value.trim();
    const resultBox = document.getElementById("agentResult");

    if (!task) {
        resultBox.textContent = "请输入任务";
        return;
    }

    const response = await fetch("/agent/run", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ task })
    });

    const data = await response.json();
    resultBox.textContent = data.data.markdown_report || data.data.final_answer;
}

document.getElementById("agentBtn").addEventListener("click", runAgent);