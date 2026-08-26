from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Playwright 定位器全能靶场</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: #f0f2f5; color: #333; }
        .card { background: white; padding: 24px; margin-bottom: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        h2 { margin-top: 0; color: #1976d2; border-bottom: 2px solid #e3f2fd; padding-bottom: 12px; font-size: 1.3em; }
        .result { margin-top: 12px; padding: 10px 14px; background: #e8f5e9; color: #2e7d32; border-radius: 6px; display: none; font-weight: bold; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

        /* 通用控件样式 */
        button, input, select { margin: 4px 0; padding: 8px 12px; border-radius: 6px; border: 1px solid #ccc; }
        button { background: #1976d2; color: white; border: none; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #1565c0; }
        button:disabled { background: #bdbdbd; cursor: not-allowed; }
        label { display: inline-block; min-width: 80px; font-weight: 500; }

        /* 故意制造的脆弱CSS类 */
        .btn-x7k9-m2.dynamic-class { background: #ff9800; }

        /* 折叠面板样式 */
        details { border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px; margin: 8px 0; }
        summary { cursor: pointer; font-weight: bold; list-style: none; }
        summary::-webkit-details-marker { display: none; }
        summary::before { content: "▶ "; font-size: 0.8em; transition: transform 0.2s; display: inline-block;}
        details[open] summary::before { transform: rotate(90deg); }

        /* 表格样式 */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #e0e0e0; padding: 10px; text-align: left; }
        th { background: #fafafa; }
    </style>
</head>
<body>
    <h1>🎯 Playwright 定位器全能靶场 v2.0</h1>
    <p style="color:#666;">💡 提示：点击任意可交互元素，下方绿色提示框出现即代表定位成功</p>

    <!-- 1. get_by_role 全覆盖 -->
    <div class="card">
        <h2>1. Role 定位 (首选 👑)</h2>
        <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
            <button>普通按钮</button>
            <a href="#" onclick="event.preventDefault(); showResult(this)">这是一个链接</a>
            <input type="text" placeholder="textbox角色" />
            <label><input type="checkbox" /> checkbox角色</label>

            <!-- menuitem 需要包裹在 menu/menuitemradio 等上下文中才更标准 -->
            <div role="menu">
                <button role="menuitem">菜单项-设置</button>
            </div>
        </div>
        <div class="result">✅ Role 基础定位成功！</div>
    </div>

    <!-- 2. Role 进阶: level & expanded -->
    <div class="card">
        <h2>2. Role 进阶技巧 (level / expanded)</h2>
        <h2 id="article-title">文章标题 (这是H2)</h2>
        <h3>副标题 (这是H3)</h3>

        <details>
            <summary>更多选项 (点击展开/折叠)</summary>
            <p>这里是折叠内容。当此区域收起时，summary 的 expanded 状态为 false。</p>
        </details>
        <div class="result">✅ Role 进阶定位成功！</div>
    </div>

    <!-- 3. get_by_text 进阶 -->
    <div class="card">
        <h2>3. Text 文本定位 (模糊/精确/正则)</h2>
        <p>欢迎回来，管理员！</p>
        <p>立即登录获取优惠</p>
        <p>用户登录状态正常</p>
        <div class="result">✅ Text 定位成功！</div>
    </div>

    <!-- 4. Label & Placeholder -->
    <div class="card">
        <h2>4. Label & Placeholder 表单定位</h2>
        <form onsubmit="event.preventDefault(); showResult(this);">
            <div><label for="email">电子邮箱</label><input id="email" type="email" /></div>
            <div style="margin-top:8px;"><input type="password" placeholder="请输入密码(无Label)" /></div>
            <button type="submit" style="margin-top:10px;">提交表单</button>
        </form>
        <div class="result">✅ 表单定位成功！</div>
    </div>

    <!-- 5. Alt & Title -->
    <div class="card">
        <h2>5. Alt & Title 属性定位</h2>
        <img src="https://via.placeholder.com/120x50?text=Logo" alt="公司官方标志" title="点击查看大图" 
             style="cursor:pointer; border-radius:6px;" onclick="showResult(this)"/>
        <div class="result">✅ Alt/Title 定位成功！</div>
    </div>

    <!-- 6. Test ID -->
    <div class="card">
        <h2>6. Test-ID 定位 (终极防御 🛡️)</h2>
        <div data-testid="user-profile-card" style="padding:12px; border:2px dashed #90caf9; border-radius:8px; cursor:pointer;"
             onclick="showResult(this)">
            🧑‍💻 用户信息卡片 (data-testid="user-profile-card")
        </div>
        <div class="result">✅ Test-ID 定位成功！</div>
    </div>

    <!-- 7. CSS/XPath 兜底 -->
    <div class="card">
        <h2>7. CSS / XPath 兜底 (不推荐 ⚠️)</h2>
        <button class="btn-x7k9-m2 dynamic-class">动态类名按钮</button>
        <div class="result">✅ CSS/XPath 兜底定位成功！</div>
    </div>

    <!-- 8. 链式、Filter、has、nth -->
    <div class="card">
        <h2>8. 进阶大招：链式 / Filter / has / nth</h2>

        <h3>📦 商品列表 (Filter & 链式)</h3>
        <ul role="list" aria-label="商品列表" style="list-style:none; padding:0;">
            <li role="listitem" style="padding:8px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <span>iPhone 15 Pro</span>
                <button name="加入购物车">购买</button>
            </li>
            <li role="listitem" style="padding:8px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <span>Playwright 实战指南</span>
                <button name="加入购物车">购买</button>
            </li>
            <li role="listitem" style="padding:8px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <span>MacBook Pro</span>
                <button name="加入购物车">购买</button>
            </li>
        </ul>

        <h3 style="margin-top:16px;">🗑️ 数据表格 (has 参数)</h3>
        <table role="table">
            <tr role="row"><th>文件名</th><th>操作</th></tr>
            <tr role="row"><td>report.pdf</td><td><button role="button">删除</button></td></tr>
            <tr role="row"><td>photo.jpg</td><td><button role="button">预览</button></td></tr>
            <tr role="row"><td>backup.zip</td><td><button role="button">删除</button></td></tr>
        </table>

        <h3 style="margin-top:16px;">👍 点赞区 (nth 索引)</h3>
        <div style="display:flex; gap:10px;">
            <button name="点赞">👍 点赞</button>
            <button name="点赞">👍 点赞</button>
            <button name="点赞">👍 点赞</button>
        </div>

        <div class="result">✅ 进阶定位成功！</div>
    </div>
        <!-- 9. Select 下拉框 -->
    <div class="card">
        <h2>9. Select 下拉框</h2>
        <form onsubmit="event.preventDefault();">
            <label for="city">选择城市</label>
            <select id="city" onchange="showResult(this)">
                <option value="beijing">北京</option>
                <option value="shanghai">上海</option>
                <option value="guangzhou">广州</option>
                <option value="shenzhen">深圳</option>
            </select>
        </form>
        <div class="result">✅ Select 定位成功！</div>
    </div>

    <!-- 13. Multi-Select 多选框 -->
<div class="card">
    <h2>13. Multi-Select 多选框</h2>
    <form onsubmit="event.preventDefault();">
        <label for="skills">选择技能（可多选）</label>
        <select id="skills" multiple size="5" onchange="showMultiResult(this)">
            <option value="python">Python</option>
            <option value="playwright">Playwright</option>
            <option value="pytest">Pytest</option>
            <option value="docker">Docker</option>
            <option value="k8s">Kubernetes</option>
        </select>
        <button type="button" id="select-all-btn" onclick="selectAllSkills()">全选</button>
    </form>
    <div class="result">✅ 已选择: 无</div>
</div>

<script>
function showMultiResult(selectEl) {
    const card = selectEl.closest('.card');
    if (!card) return;
    const resultDiv = card.querySelector('.result');
    if (!resultDiv) return;

    // 更新文本
    const selected = Array.from(selectEl.selectedOptions).map(opt => opt.value);
    resultDiv.textContent = selected.length === 0 ? '✅ 已选择: 无' : `✅ 已选择: ${selected.join(', ')}`;

    // 显示并设置自动隐藏（复用 showResult 的逻辑）
    if (card._hideTimer) clearTimeout(card._hideTimer);
    resultDiv.style.display = 'block';
    card._hideTimer = setTimeout(() => {
        resultDiv.style.display = 'none';
    }, 3000);
}

function selectAllSkills() {
    const selectEl = document.getElementById('skills');
    Array.from(selectEl.options).forEach(opt => opt.selected = true);
    showMultiResult(selectEl);
}
</script>

    <!-- 10. Radio 单选框 -->
    <div class="card">
        <h2>10. Radio 单选框</h2>
        <div>
            <label><input type="radio" name="gender" value="male" onchange="showResult(this)"> 男</label>
            <label><input type="radio" name="gender" value="female" onchange="showResult(this)"> 女</label>
            <label><input type="radio" name="gender" value="other" onchange="showResult(this)"> 其他</label>
        </div>
        <div class="result">✅ Radio 定位成功！</div>
    </div>

        <!-- 11. Hover 悬停菜单（修复闪烁） -->
    <div class="card">
        <h2>11. Hover 悬停菜单</h2>
        <div id="hover-container" style="position: relative; display: inline-block;">
            <button id="user-menu">👤 用户</button>
            <div id="dropdown" style="display: none; position: absolute; background: white; border: 1px solid #ccc; border-radius: 6px; padding: 8px 0; min-width: 120px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); z-index: 100;">
                <div style="padding: 8px 16px; cursor: pointer;" onclick="showResult(this); document.getElementById('dropdown').style.display='none'">个人中心</div>
                <div style="padding: 8px 16px; cursor: pointer;" onclick="showResult(this); document.getElementById('dropdown').style.display='none'">设置</div>
                <div style="padding: 8px 16px; cursor: pointer;" onclick="showResult(this); document.getElementById('dropdown').style.display='none'">退出登录</div>
            </div>
        </div>
        <script>
            (function() {
                const container = document.getElementById('hover-container');
                const dropdown = document.getElementById('dropdown');
                let timer = null;
                container.addEventListener('mouseenter', function() {
                    if (timer) clearTimeout(timer);
                    dropdown.style.display = 'block';
                });
                container.addEventListener('mouseleave', function() {
                    timer = setTimeout(function() {
                        dropdown.style.display = 'none';
                    }, 200);
                });
                // 点击菜单项自动隐藏
                dropdown.addEventListener('click', function(e) {
                    if (e.target.closest('div')) {
                        dropdown.style.display = 'none';
                    }
                });
            })();
        </script>
        <div class="result">✅ Hover 定位成功！</div>
    </div>
    
                        <!-- 12. iframe 内嵌框架 (frame_locator) -->
    <div class="card">
        <h2>12. iframe 内嵌框架</h2>
        
        <template id="iframe-content-12">
            <style>
                body { font-family: sans-serif; padding: 15px; }
                .msg { padding: 10px; margin-top: 10px; border-radius: 4px; display: none; }
                .success { color: #2e7d32; background: #e8f5e9; }
                .error { color: #c62828; background: #ffebee; }
            </style>
            
            <label for="username">用户名</label>
            <input type="text" id="username" placeholder="输入用户名" />
            <button id="submit-btn">提交</button>
            
            <!-- 成功与错误提示分离，避免状态混乱 -->
            <div id="result-success" class="msg success">✅ iframe 定位成功！</div>
            <div id="result-error" class="msg error">⚠️ 请输入用户名后再提交</div>
            
            <script>
                document.getElementById('submit-btn').addEventListener('click', function() {
                    var name = document.getElementById('username').value.trim();
                    var successEl = document.getElementById('result-success');
                    var errorEl = document.getElementById('result-error');
                    
                    // 每次点击先重置所有状态
                    successEl.style.display = 'none';
                    errorEl.style.display = 'none';
                    
                    if (name === '') {
                        // 空输入：显示错误提示
                        errorEl.style.display = 'block';
                    } else {
                        // 有输入：显示成功提示，3秒后自动消失
                        successEl.style.display = 'block';
                        setTimeout(function() {
                            successEl.style.display = 'none';
                        }, 3000);
                    }
                });
            </script>
        </template>

        <iframe id="my-iframe-12" style="width:100%; height:200px; border:1px solid #ccc; border-radius:4px;"></iframe>

        <script>
            (function(){
                var tpl = document.getElementById('iframe-content-12');
                var iframe = document.getElementById('my-iframe-12');
                iframe.srcdoc = tpl.innerHTML;
            })();
        </script>

        <div class="result">✅ iframe 卡片触发成功（父页面）</div>
    </div>
    
    <script>
        // ✅ 修复：每个卡片维护独立的定时器引用，重复触发时重置
function showResult(el) {
    const card = el.closest('.card');
    if (!card) return;
    
    const res = card.querySelector('.result');
    if (!res) return;
    
    // 清除之前的隐藏定时器（关键修复！）
    if (card._hideTimer) {
        clearTimeout(card._hideTimer);
    }
    
    res.style.display = 'block';
    
    // 重新设置3秒隐藏
    card._hideTimer = setTimeout(() => {
        res.style.display = 'none';
    }, 3000);
}

        // 为所有可交互元素绑定事件
        document.querySelectorAll('button, a, input, img, [data-testid], details > summary').forEach(el => {
            el.addEventListener('click', () => showResult(el));
        });
        // checkbox change 事件
        document.querySelectorAll('input[type="checkbox"]').forEach(el => {
            el.addEventListener('change', () => showResult(el));
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


if __name__ == "__main__":
    print("🚀 靶场已启动: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)