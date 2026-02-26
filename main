# =========================================================
# نظام إدارة أصول تكنولوجيا المعلومات - Streamlit Version
# الهيئة القومية لسلامة الغذاء - إدارة تكنولوجيا المعلومات
# Created by Eng Ahmed Waheed
# =========================================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re

# =========================================================
# إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="نظام إدارة الأصول - الهيئة القومية لسلامة الغذاء",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# إعدادات قاعدة البيانات
# =========================================================
DB_NAME = "nfsa_assets.db"

def get_db_connection():
    """إنشاء اتصال آمن بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات مع دعم الترقية التلقائية"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'technician',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )''')
    
    # جدول الإدارات
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # جدول الموظفين
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        dept_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dept_id) REFERENCES departments(id)
    )''')
    
    # جدول الأجهزة
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        serial_device TEXT NOT NULL UNIQUE,
        serial_monitor TEXT,
        mac_address TEXT,
        specs TEXT,
        status TEXT DEFAULT 'تعمل',
        employee_id INTEGER,
        purchase_date DATE,
        warranty_end DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )''')
    
    # جدول التذاكر
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        employee_id INTEGER,
        issue_desc TEXT NOT NULL,
        priority TEXT DEFAULT 'عادي',
        status TEXT DEFAULT 'مفتوح',
        action_taken TEXT,
        cost REAL,
        tech_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY(device_id) REFERENCES devices(id),
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )''')
    
    # جدول سجل النشاطات
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        table_name TEXT,
        record_id INTEGER,
        ip_address TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # ترقية الجداول القديمة
    for col, table in [
        ('mac_address TEXT', 'devices'),
        ('created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'devices'),
        ('purchase_date DATE', 'devices'),
        ('warranty_end DATE', 'devices'),
        ('priority TEXT DEFAULT \'عادي\'', 'tickets'),
        ('resolved_at TIMESTAMP', 'tickets'),
        ('last_login TIMESTAMP', 'users'),
        ('is_active INTEGER DEFAULT 1', 'users'),
    ]:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
        except:
            pass
    
    # إنشاء مدير افتراضي
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    if c.fetchone()[0] == 0:
        admin_hash = generate_password_hash('Admin@123')
        c.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                  ('admin', admin_hash, 'مدير النظام', 'admin'))
    
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات عند البدء
init_db()

# =========================================================
# دوال الأمان والمساعدة
# =========================================================

def log_activity(user_id, action, table_name=None, record_id=None):
    """تسجيل النشاطات للأمان"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        ip = st.context.headers.get("X-Forwarded-For", st.context.headers.get("Remote-Addr", "unknown"))
        c.execute("INSERT INTO audit_log (user_id, action, table_name, record_id, ip_address) VALUES (?, ?, ?, ?, ?)",
                  (user_id, action, table_name, record_id, ip))
        conn.commit()
        conn.close()
    except:
        pass

def validate_mac_address(mac):
    """التحقق من صحة MAC Address"""
    if not mac:
        return True
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None

def check_session_timeout():
    """التحقق من انتهاء الجلسة"""
    if 'last_activity' in st.session_state:
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > timedelta(minutes=30):
            st.session_state.clear()
            st.warning('انتهت الجلسة بسبب عدم النشاط')
            st.rerun()
    st.session_state.last_activity = datetime.now()

# =========================================================
# واجهة المستخدم - الهيدر والفوتر
# =========================================================

def render_header():
    """عرض الهيدر الموحد"""
    st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .footer {
        background: #34495e;
        color: #bdc3c7;
        text-align: center;
        padding: 10px;
        margin-top: 40px;
        border-radius: 10px;
        font-size: 0.9em;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        border-right: 4px solid #3498db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header"><h2>🛡️ الهيئة القومية لسلامة الغذاء</h2><h4>إدارة تكنولوجيا المعلومات</h4></div>', unsafe_allow_html=True)

def render_footer():
    """عرض الفوتر الموحد"""
    st.markdown('<div class="footer">created by Eng ahmed waheed</div>', unsafe_allow_html=True)

# =========================================================
# صفحة تسجيل الدخول
# =========================================================

def login_page():
    """صفحة تسجيل الدخول"""
    render_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        
        # اختيار نوع الدخول
        login_type = st.radio("نوع الدخول", ["🔐 دخول المسئولين", "👤 دخول الموظف (بكود الجهاز)"], horizontal=True)
        
        if login_type == "🔐 دخول المسئولين":
            username = st.text_input("اسم المستخدم", key="login_user")
            password = st.text_input("كلمة المرور", type="password", key="login_pass")
            
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
                user = c.fetchone()
                conn.close()
                
                if user and check_password_hash(user['password_hash'], password):
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.session_state.full_name = user['full_name']
                    st.session_state.last_activity = datetime.now()
                    st.session_state.user_type = 'admin'
                    
                    log_activity(user['id'], 'LOGIN', 'users', user['id'])
                    st.success(f'مرحباً بك يا {user["full_name"]}')
                    st.rerun()
                else:
                    st.error('اسم المستخدم أو كلمة المرور غير صحيحة')
        
        else:  # دخول الموظف
            device_code = st.text_input("أدخل سريال الجهاز", key="device_login", placeholder="مثال: SN123456")
            
            if st.button("دخول", type="primary", use_container_width=True):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM devices WHERE serial_device = ?", (device_code,))
                device = c.fetchone()
                conn.close()
                
                if device:
                    st.session_state.device_id = device['id']
                    st.session_state.device_serial = device['serial_device']
                    st.session_state.user_type = 'employee'
                    st.session_state.last_activity = datetime.now()
                    
                    log_activity(None, 'EMPLOYEE_LOGIN', 'devices', device['id'])
                    st.success('تم تسجيل الدخول بنجاح')
                    st.rerun()
                else:
                    st.error('كود الجهاز غير صحيح')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    render_footer()

# =========================================================
# لوحة التحكم (Dashboard)
# =========================================================

def dashboard_page():
    """لوحة التحكم الرئيسية"""
    render_header()
    
    # شريط جانبي للملاحة
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('full_name', '')}")
        st.markdown(f"*{'مدير نظام' if st.session_state.get('user_role') == 'admin' else 'فني صيانة'}*")
        st.divider()
        
        page = st.radio("القائمة", [
            "📊 لوحة التحكم",
            "💻 إدارة الأجهزة",
            "🎫 التذاكر والصيانة",
            "📈 التقارير",
            "👥 الموظفين",
            "🏢 الإدارات",
        ] + (["🔐 إدارة المستخدمين", "📋 سجل النشاطات"] if st.session_state.get('user_role') == 'admin' else []),
        index=0)
        
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            if 'user_id' in st.session_state:
                log_activity(st.session_state.user_id, 'LOGOUT', 'users', st.session_state.user_id)
            st.session_state.clear()
            st.rerun()
    
    # محتوى الصفحة حسب الاختيار
    if page == "📊 لوحة التحكم":
        show_dashboard_stats()
    elif page == "💻 إدارة الأجهزة":
        show_devices_page()
    elif page == "🎫 التذاكر والصيانة":
        show_tickets_page()
    elif page == "📈 التقارير":
        show_reports_page()
    elif page == "👥 الموظفين":
        show_employees_page()
    elif page == "🏢 الإدارات":
        show_departments_page()
    elif page == "🔐 إدارة المستخدمين" and st.session_state.get('user_role') == 'admin':
        show_users_page()
    elif page == "📋 سجل النشاطات" and st.session_state.get('user_role') == 'admin':
        show_audit_log_page()
    
    render_footer()

def show_dashboard_stats():
    """عرض إحصائيات لوحة التحكم"""
    conn = get_db_connection()
    
    # الإحصائيات
    stats = {
        'total_devices': pd.read_sql("SELECT COUNT(*) as c FROM devices", conn)['c'][0],
        'total_tickets': pd.read_sql("SELECT COUNT(*) as c FROM tickets", conn)['c'][0],
        'open_tickets': pd.read_sql("SELECT COUNT(*) as c FROM tickets WHERE status = 'مفتوح'", conn)['c'][0],
        'total_emps': pd.read_sql("SELECT COUNT(*) as c FROM employees", conn)['c'][0],
        'maintenance_devices': pd.read_sql("SELECT COUNT(*) as c FROM devices WHERE status = 'تحت الصيانة'", conn)['c'][0],
        'total_cost': pd.read_sql("SELECT COALESCE(SUM(cost), 0) as c FROM tickets", conn)['c'][0]
    }
    conn.close()
    
    # عرض البطاقات
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📱 إجمالي الأجهزة", stats['total_devices'])
    with col2:
        st.metric("🎫 تذاكر مفتوحة", stats['open_tickets'], delta=f"-{stats['total_tickets'] - stats['open_tickets']} مغلقة")
    with col3:
        st.metric("👥 الموظفين", stats['total_emps'])
    with col4:
        st.metric("🔧 تحت الصيانة", stats['maintenance_devices'])
    
    # رسوم بيانية
    col1, col2 = st.columns(2)
    
    with col1:
        conn = get_db_connection()
        df_types = pd.read_sql("SELECT type, COUNT(*) as count FROM devices GROUP BY type", conn)
        conn.close()
        if not df_types.empty:
            fig = px.pie(df_types, values='count', names='type', title='توزيع الأجهزة حسب النوع', color_discrete_sequence=px.colors.sequential.Blues)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        conn = get_db_connection()
        df_status = pd.read_sql("SELECT status, COUNT(*) as count FROM tickets GROUP BY status", conn)
        conn.close()
        if not df_status.empty:
            fig = px.bar(df_status, x='status', y='count', title='حالة التذاكر', color='count', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
    
    # آخر التذاكر
    st.subheader("🕐 آخر التذاكر")
    conn = get_db_connection()
    recent = pd.read_sql("""
        SELECT t.id, d.serial_device, t.issue_desc, t.priority, t.status, t.created_at
        FROM tickets t 
        LEFT JOIN devices d ON t.device_id = d.id 
        ORDER BY t.created_at DESC LIMIT 10
    """, conn)
    conn.close()
    
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد تذاكر حديثة")

# =========================================================
# صفحة الأجهزة
# =========================================================

def show_devices_page():
    """صفحة إدارة الأجهزة"""
    st.subheader("💻 إدارة الأجهزة")
    
    # نموذج إضافة جهاز
    with st.expander("➕ إضافة جهاز جديد", expanded=False):
        with st.form("add_device_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                device_type = st.selectbox("نوع الجهاز", ["Laptop", "Desktop", "Printer", "Scanner"])
                serial_device = st.text_input("سريال الجهاز *")
                serial_monitor = st.text_input("سريال الشاشة")
            with col2:
                mac_address = st.text_input("MAC Address", placeholder="00:1A:2B:3C:4D:5E")
                specs = st.text_area("المواصفات", placeholder="RAM: 8GB, CPU: i5, Storage: 256GB SSD")
                status = st.selectbox("الحالة", ["تعمل", "تحت الصيانة", "تالفة", "مخزنة"])
            with col3:
                conn = get_db_connection()
                employees = pd.read_sql("SELECT id, name FROM employees", conn)
                conn.close()
                emp_options = {f"{row['name']}": row['id'] for _, row in employees.iterrows()} if not employees.empty else {}
                selected_emp = st.selectbox("عهدة موظف", ["-- بدون عهدة --"] + list(emp_options.keys()))
                employee_id = emp_options.get(selected_emp) if selected_emp != "-- بدون عهدة --" else None
                purchase_date = st.date_input("تاريخ الشراء", value=None, format="YYYY-MM-DD")
                warranty_end = st.date_input("نهاية الضمان", value=None, format="YYYY-MM-DD")
            
            submitted = st.form_submit_button("💾 حفظ الجهاز", type="primary")
            
            if submitted:
                if not serial_device:
                    st.error("سريال الجهاز مطلوب")
                elif mac_address and not validate_mac_address(mac_address):
                    st.error("صيغة MAC Address غير صحيحة (مثال: 00:1A:2B:3C:4D:5E)")
                else:
                    try:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""INSERT INTO devices 
                            (type, serial_device, serial_monitor, mac_address, specs, status, employee_id, purchase_date, warranty_end) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (device_type, serial_device, serial_monitor, mac_address, specs, status, employee_id, 
                             purchase_date if purchase_date else None, warranty_end if warranty_end else None))
                        conn.commit()
                        log_activity(st.session_state.get('user_id'), 'CREATE_DEVICE', 'devices')
                        conn.close()
                        st.success("✅ تم تسجيل الجهاز بنجاح")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ سريال الجهاز مسجل بالفعل")
    
    # بحث وعرض الأجهزة
    search = st.text_input("🔍 بحث", placeholder="ابحث بالسريال أو MAC Address...")
    
    conn = get_db_connection()
    if search:
        devices = pd.read_sql("""
            SELECT d.id, d.type, d.serial_device, d.serial_monitor, d.mac_address, d.specs, d.status, e.name as emp_name
            FROM devices d LEFT JOIN employees e ON d.employee_id = e.id
            WHERE d.serial_device LIKE ? OR d.mac_address LIKE ? OR d.specs LIKE ?
            ORDER BY d.created_at DESC
        """, conn, params=[f'%{search}%', f'%{search}%', f'%{search}%'])
    else:
        devices = pd.read_sql("""
            SELECT d.id, d.type, d.serial_device, d.serial_monitor, d.mac_address, d.specs, d.status, e.name as emp_name
            FROM devices d LEFT JOIN employees e ON d.employee_id = e.id
            ORDER BY d.created_at DESC
        """, conn)
    conn.close()
    
    if not devices.empty:
        # تنسيق العرض
        def color_status(status):
            if status == 'تعمل': return '🟢'
            elif status == 'تحت الصيانة': return '🟡'
            elif status == 'تالفة': return '🔴'
            return '⚪'
        
        devices['الحالة'] = devices['status'].apply(color_status)
        devices['MAC Address'] = devices['mac_address'].apply(lambda x: f"`{x}`" if x else "-")
        devices['سريال الجهاز'] = devices['serial_device'].apply(lambda x: f"`{x}`")
        
        st.dataframe(
            devices[['type', 'سريال الجهاز', 'serial_monitor', 'MAC Address', 'emp_name', 'الحالة', 'specs']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "type": "النوع",
                "سريال الجهاز": "سريال الجهاز",
                "serial_monitor": "سريال الشاشة",
                "MAC Address": st.column_config.TextColumn("MAC Address"),
                "emp_name": "الموظف",
                "الحالة": "الحالة",
                "specs": "المواصفات"
            }
        )
        
        # زر التصدير
        st.download_button(
            "📥 تصدير إلى Excel",
            devices.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"devices_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("لا توجد أجهزة مسجلة")

# =========================================================
# صفحة التذاكر
# =========================================================

def show_tickets_page():
    """صفحة إدارة التذاكر"""
    st.subheader("🎫 إدارة التذاكر والصيانة")
    
    # إنشاء تذكرة جديدة
    with st.expander("➕ إنشاء تذكرة صيانة جديدة", expanded=False):
        with st.form("new_ticket_form"):
            col1, col2 = st.columns(2)
            with col1:
                conn = get_db_connection()
                devices = pd.read_sql("SELECT id, type, serial_device FROM devices WHERE status != 'تحت الصيانة'", conn)
                conn.close()
                if not devices.empty:
                    device_options = {f"{row['type']} - {row['serial_device']}": row['id'] for _, row in devices.iterrows()}
                    selected = st.selectbox("اختر الجهاز", list(device_options.keys()))
                    device_id = device_options[selected]
                else:
                    st.warning("لا توجد أجهزة متاحة للصيانة")
                    device_id = None
                priority = st.selectbox("الأولوية", ["عادي", "متوسط", "عاجل"])
            with col2:
                issue_desc = st.text_area("وصف المشكلة *", height=100)
            
            submitted = st.form_submit_button("🎫 إنشاء التذكرة", type="primary")
            
            if submitted and device_id and issue_desc:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO tickets (device_id, issue_desc, priority, status) VALUES (?, ?, ?, 'مفتوح')",
                         (device_id, issue_desc, priority))
                c.execute("UPDATE devices SET status = 'تحت الصيانة' WHERE id = ?", (device_id,))
                conn.commit()
                log_activity(st.session_state.get('user_id'), 'CREATE_TICKET', 'tickets')
                conn.close()
                st.success("✅ تم إنشاء التذكرة بنجاح")
                st.rerun()
    
    # فلترة وعرض التذاكر
    col1, col2 = st.columns([3, 1])
    with col2:
        status_filter = st.selectbox("فلترة حسب الحالة", ["الكل", "مفتوح", "قيد العمل", "مغلق"])
    
    conn = get_db_connection()
    if status_filter == "الكل":
        tickets = pd.read_sql("""
            SELECT t.id, d.serial_device, d.mac_address, e.name as emp_name, t.issue_desc, 
                   t.priority, t.status, t.tech_name, t.cost, t.created_at
            FROM tickets t 
            LEFT JOIN devices d ON t.device_id = d.id 
            LEFT JOIN employees e ON t.employee_id = e.id 
            ORDER BY t.created_at DESC
        """, conn)
    else:
        tickets = pd.read_sql("""
            SELECT t.id, d.serial_device, d.mac_address, e.name as emp_name, t.issue_desc, 
                   t.priority, t.status, t.tech_name, t.cost, t.created_at
            FROM tickets t 
            LEFT JOIN devices d ON t.device_id = d.id 
            LEFT JOIN employees e ON t.employee_id = e.id 
            WHERE t.status = ?
            ORDER BY t.created_at DESC
        """, conn, params=[status_filter])
    conn.close()
    
    if not tickets.empty:
        # أزرار الإجراءات لكل تذكرة
        for _, ticket in tickets.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 2])
                with c1:
                    st.markdown(f"**الجهاز:** `{ticket['serial_device']}`")
                    st.markdown(f"*MAC:* `{ticket['mac_address'] or '-'}`")
                with c2:
                    st.markdown(f"**الموظف:** {ticket['emp_name'] or 'غير محدد'}")
                    st.markdown(f"**الأولوية:** {'🔴 عاجل' if ticket['priority']=='عاجل' else '🟡 متوسط' if ticket['priority']=='متوسط' else '🟢 عادي'}")
                with c3:
                    status_color = "🟡" if ticket['status']=='مفتوح' else "🔵" if ticket['status']=='قيد العمل' else "🟢"
                    st.markdown(f"**الحالة:** {status_color} {ticket['status']}")
                with c4:
                    st.markdown(f"**التكلفة:** {ticket['cost'] or 0} ج.م")
                with c5:
                    if ticket['status'] != 'مغلق':
                        with st.popover("✅ حل"):
                            with st.form(f"resolve_{ticket['id']}"):
                                action = st.text_area("الإجراء المتخذ", key=f"action_{ticket['id']}")
                                cost = st.number_input("التكلفة", min_value=0.0, step=0.01, key=f"cost_{ticket['id']}")
                                if st.form_submit_button("إغلاق"):
                                    conn = get_db_connection()
                                    c = conn.cursor()
                                    c.execute("""UPDATE tickets SET action_taken = ?, cost = ?, tech_name = ?, 
                                                status = 'مغلق', resolved_at = CURRENT_TIMESTAMP WHERE id = ?""",
                                            (action, cost, st.session_state.get('full_name'), ticket['id']))
                                    c.execute("UPDATE devices SET status = 'تعمل' WHERE id = (SELECT device_id FROM tickets WHERE id = ?)", (ticket['id'],))
                                    conn.commit()
                                    log_activity(st.session_state.get('user_id'), 'RESOLVE_TICKET', 'tickets', ticket['id'])
                                    conn.close()
                                    st.success("تم إغلاق التذكرة")
                                    st.rerun()
                    else:
                        st.markdown(f"🔧 الفني: {ticket['tech_name'] or '-'}")
                
                st.markdown(f"📝 **المشكلة:** {ticket['issue_desc']}")
                st.caption(f"🕐 {ticket['created_at']}")
    else:
        st.info("لا توجد تذاكر")

# =========================================================
# صفحة الموظف (دخول بكود الجهاز)
# =========================================================

def employee_ticket_page():
    """صفحة الموظف للإبلاغ عن المشاكل"""
    render_header()
    
    if 'device_serial' not in st.session_state:
        st.warning("يرجى تسجيل الدخول أولاً")
        login_page()
        return
    
    check_session_timeout()
    
    # معلومات الجهاز
    conn = get_db_connection()
    device = pd.read_sql("SELECT * FROM devices WHERE id = ?", conn, params=[st.session_state.device_id]).iloc[0]
    my_tickets = pd.read_sql("SELECT * FROM tickets WHERE device_id = ? ORDER BY created_at DESC", conn, params=[st.session_state.device_id])
    conn.close()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"📱 معلومات جهازك: `{device['serial_device']}`")
        st.info(f"""
        - **النوع:** {device['type']}
        - **سريال الشاشة:** {device['serial_monitor'] or '-'}
        - **MAC Address:** `{device['mac_address'] or '-'}`
        - **المواصفات:** {device['specs'] or '-'}
        - **الحالة:** {'🟢 تعمل' if device['status'] == 'تعمل' else '🟡 تحت الصيانة'}
        """)
    
    with col2:
        st.subheader("🚨 الإبلاغ عن مشكلة")
        with st.form("employee_ticket"):
            issue = st.text_area("وصف المشكلة *", height=100)
            priority = st.selectbox("الأولوية", ["عادي", "متوسط", "عاجل"])
            if st.form_submit_button("📤 إرسال البلاغ", type="primary"):
                if issue:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO tickets (device_id, issue_desc, priority, status) VALUES (?, ?, ?, 'مفتوح')",
                             (st.session_state.device_id, issue, priority))
                    c.execute("UPDATE devices SET status = 'تحت الصيانة' WHERE id = ?", (st.session_state.device_id,))
                    conn.commit()
                    conn.close()
                    st.success("✅ تم إرسال البلاغ بنجاح")
                    st.rerun()
                else:
                    st.error("يرجى وصف المشكلة")
    
    # تذاكري السابقة
    st.divider()
    st.subheader("📋 تذاكري السابقة")
    if not my_tickets.empty:
        for _, t in my_tickets.iterrows():
            with st.container(border=True):
                st.markdown(f"**#{t['id']}** - {t['issue_desc']}")
                st.markdown(f"الأولوية: {'🔴' if t['priority']=='عاجل' else '🟡' if t['priority']=='متوسط' else '🟢'} {t['priority']}")
                st.markdown(f"الحالة: {'🟡' if t['status']=='مفتوح' else '🟢'} {t['status']}")
                if t['action_taken']:
                    st.markdown(f"✅ الإجراء: {t['action_taken']}")
                st.caption(f"🕐 {t['created_at']}")
    else:
        st.info("لا توجد تذاكر سابقة")
    
    if st.button("🚪 خروج"):
        st.session_state.clear()
        st.rerun()
    
    render_footer()

# =========================================================
# الصفحات الأخرى (مبسطة)
# =========================================================

def show_reports_page():
    """صفحة التقارير"""
    st.subheader("📈 التقارير والإحصائيات")
    
    conn = get_db_connection()
    
    # إحصائيات
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total = pd.read_sql("SELECT COUNT(*) as c FROM devices", conn)['c'][0]
        st.metric("إجمالي الأجهزة", total)
    with col2:
        tickets = pd.read_sql("SELECT COUNT(*) as c FROM tickets", conn)['c'][0]
        st.metric("إجمالي التذاكر", tickets)
    with col3:
        cost = pd.read_sql("SELECT COALESCE(SUM(cost), 0) as c FROM tickets", conn)['c'][0]
        st.metric("تكلفة الصيانة", f"{cost} ج.م")
    with col4:
        avg = pd.read_sql("SELECT AVG(julianday(resolved_at) - julianday(created_at)) as c FROM tickets WHERE resolved_at IS NOT NULL", conn)['c'][0]
        st.metric("متوسط وقت الحل", f"{avg or 0:.1f} يوم")
    
    # رسوم بيانية
    col1, col2 = st.columns(2)
    
    with col1:
        df = pd.read_sql("SELECT type, COUNT(*) as count FROM devices GROUP BY type", conn)
        if not df.empty:
            fig = px.pie(df, values='count', names='type', title='توزيع الأجهزة')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df = pd.read_sql("SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority", conn)
        if not df.empty:
            fig = px.bar(df, x='priority', y='count', title='التذاكر حسب الأولوية', color='count')
            st.plotly_chart(fig, use_container_width=True)
    
    # الأجهزة الأكثر صيانة
    st.subheader("🔧 الأجهزة الأكثر صيانة")
    top = pd.read_sql("""
        SELECT d.serial_device, d.type, COUNT(t.id) as count 
        FROM devices d LEFT JOIN tickets t ON d.id = t.device_id 
        GROUP BY d.id ORDER BY count DESC LIMIT 10
    """, conn)
    conn.close()
    
    if not top.empty:
        st.dataframe(top, use_container_width=True, hide_index=True)
    
    # زر الطباعة
    st.download_button("🖨️ طباعة التقرير", "تقرير نظام إدارة الأصول", file_name="report.txt")

def show_employees_page():
    """صفحة الموظفين"""
    st.subheader("👥 إدارة الموظفين")
    
    with st.expander("➕ إضافة موظف"):
        with st.form("add_emp"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("اسم الموظف *")
                email = st.text_input("البريد الإلكتروني *")
            with col2:
                phone = st.text_input("رقم الهاتف")
                conn = get_db_connection()
                depts = pd.read_sql("SELECT id, name FROM departments", conn)
                conn.close()
                dept_opts = {row['name']: row['id'] for _, row in depts.iterrows()} if not depts.empty else {}
                dept = st.selectbox("الإدارة", ["-- اختر --"] + list(dept_opts.keys()))
            with col3:
                st.empty()  # spacer
                if st.form_submit_button("💾 حفظ"):
                    if name and email:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO employees (name, email, phone, dept_id) VALUES (?, ?, ?, ?)",
                                 (name, email, phone, dept_opts.get(dept) if dept != "-- اختر --" else None))
                        conn.commit()
                        log_activity(st.session_state.get('user_id'), 'CREATE_EMPLOYEE', 'employees')
                        conn.close()
                        st.success("تم الإضافة")
                        st.rerun()
    
    conn = get_db_connection()
    emps = pd.read_sql("""
        SELECT e.id, e.name, e.email, e.phone, d.name as dept
        FROM employees e LEFT JOIN departments d ON e.dept_id = d.id
    """, conn)
    conn.close()
    
    if not emps.empty:
        st.dataframe(emps, use_container_width=True, hide_index=True)

def show_departments_page():
    """صفحة الإدارات"""
    st.subheader("🏢 إدارة الإدارات")
    
    with st.form("add_dept"):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            name = st.text_input("اسم الإدارة *")
        with col2:
            dtype = st.selectbox("النوع", ["عامة", "مركزية"])
        with col3:
            if st.form_submit_button("➕ إضافة"):
                if name:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO departments (name, type) VALUES (?, ?)", (name, dtype))
                    conn.commit()
                    conn.close()
                    st.success("تمت الإضافة")
                    st.rerun()
    
    conn = get_db_connection()
    depts = pd.read_sql("SELECT * FROM departments", conn)
    conn.close()
    
    if not depts.empty:
        st.dataframe(depts, use_container_width=True, hide_index=True)

def show_users_page():
    """صفحة إدارة المستخدمين (للمديرين)"""
    if st.session_state.get('user_role') != 'admin':
        st.warning("غير مصرح")
        return
    
    st.subheader("🔐 إدارة المستخدمين")
    
    with st.expander("➕ إضافة مستخدم جديد"):
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("اسم المستخدم *")
                password = st.text_input("كلمة المرور *", type="password")
                full_name = st.text_input("الاسم الكامل *")
            with col2:
                email = st.text_input("البريد الإلكتروني")
                role = st.selectbox("الصلاحية", ["technician", "admin"], format_func=lambda x: "مدير" if x=="admin" else "فني")
            
            if st.form_submit_button("💾 حفظ"):
                if username and password and full_name:
                    try:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                                 (username, generate_password_hash(password), full_name, email, role))
                        conn.commit()
                        log_activity(st.session_state.user_id, 'CREATE_USER', 'users')
                        conn.close()
                        st.success("تم إضافة المستخدم")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("اسم المستخدم موجود")
    
    conn = get_db_connection()
    users = pd.read_sql("SELECT id, username, full_name, email, role, created_at, last_login FROM users", conn)
    conn.close()
    
    if not users.empty:
        users['role'] = users['role'].apply(lambda x: "🔴 مدير" if x=="admin" else "🔵 فني")
        st.dataframe(users, use_container_width=True, hide_index=True)

def show_audit_log_page():
    """صفحة سجل النشاطات"""
    if st.session_state.get('user_role') != 'admin':
        st.warning("غير مصرح")
        return
    
    st.subheader("📋 سجل النشاطات (Audit Log)")
    
    conn = get_db_connection()
    logs = pd.read_sql("""
        SELECT a.id, u.username, a.action, a.table_name, a.record_id, a.ip_address, a.timestamp
        FROM audit_log a LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC LIMIT 100
    """, conn)
    conn.close()
    
    if not logs.empty:
        st.dataframe(logs, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد سجلات")

# =========================================================
# الصفحة الرئيسية (Router)
# =========================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    # تهيئة الجلسة
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
    
    # توجيه حسب حالة الدخول
    if 'user_type' not in st.session_state:
        login_page()
    elif st.session_state.user_type == 'employee':
        check_session_timeout()
        employee_ticket_page()
    else:
        check_session_timeout()
        dashboard_page()

if __name__ == "__main__":
    print("=" * 60)
    print("نظام إدارة أصول تكنولوجيا المعلومات - Streamlit")
    print("الهيئة القومية لسلامة الغذاء")
    print("Created by Eng Ahmed Waheed")
    print("=" * 60)
    print("تشغيل على: http://10.1.1.25:8080")
    print("admin / Admin@123")
    print("=" * 60)
    
    main()
