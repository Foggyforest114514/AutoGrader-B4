# AutoGrader API

基于FastAPI的AutoGrader在线评测系统后端API服务。

## 项目结构

```
autograder_api/
├── app/
│   ├── models/
│   │   └── models.py          # 数据库模型
│   ├── routers/
│   │   ├── auth.py            # 认证路由
│   │   ├── users.py           # 用户管理路由
│   │   ├── courses.py         # 课程管理路由
│   │   ├── classes.py         # 班级管理路由
│   │   ├── assignments.py     # 作业管理路由
│   │   ├── submissions.py     # 提交管理路由
│   │   └── grades.py          # 成绩管理路由
│   ├── __init__.py
│   ├── main.py                # 主应用文件
│   ├── database.py            # 数据库配置
│   ├── schemas.py             # 数据验证模型
│   └── auth.py                # 认证模块
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

## 功能特性

- ✅ 用户认证与授权（JWT Token）
- ✅ 用户管理（学生、教师、管理员）
- ✅ 课程管理
- ✅ 班级管理
- ✅ 作业管理
- ✅ 代码提交与评测
- ✅ 成绩管理
- ✅ RESTful API设计
- ✅ 自动API文档（Swagger UI）

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL
- **ORM**: SQLAlchemy
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt
- **数据验证**: Pydantic

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息：

```
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/autograder
SECRET_KEY=your-secret-key
```

### 3. 初始化数据库

确保MySQL数据库已创建，然后运行：

```bash
python -c "from app.database import init_db; init_db()"
```

### 4. 运行服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或直接运行：

```bash
python app/main.py
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口说明

### 认证接口

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新Token
- `POST /api/v1/auth/reset-password` - 重置密码

### 用户接口

- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me` - 修改当前用户信息
- `GET /api/v1/users` - 管理员获取用户列表
- `POST /api/v1/users` - 管理员创建教师账号
- `POST /api/v1/users/{id}/deactivate` - 停用账号

### 课程接口

- `GET /api/v1/courses` - 获取课程列表
- `POST /api/v1/courses` - 创建课程
- `GET /api/v1/courses/{id}` - 获取课程详情
- `PUT /api/v1/courses/{id}` - 修改课程
- `DELETE /api/v1/courses/{id}` - 删除课程

### 班级接口

- `GET /api/v1/classes` - 获取班级列表
- `POST /api/v1/classes` - 创建班级
- `GET /api/v1/classes/{id}/students` - 查看班级学生
- `POST /api/v1/classes/{id}/students` - 手动添加学生
- `POST /api/v1/classes/{id}/students/import` - 批量导入学生
- `DELETE /api/v1/classes/{id}/students/{sid}` - 移除学生

### 作业接口

- `GET /api/v1/assignments` - 获取作业列表
- `POST /api/v1/assignments` - 创建作业
- `GET /api/v1/assignments/{id}` - 获取作业详情
- `PUT /api/v1/assignments/{id}` - 修改作业
- `POST /api/v1/assignments/{id}/publish` - 发布作业

### 提交接口

- `POST /api/v1/submissions` - 提交作业
- `GET /api/v1/submissions/{id}` - 获取提交详情
- `PATCH /api/v1/submissions/{id}/result` - 更新评测结果（B-2模块调用）
- `GET /api/v1/submissions/my` - 获取我的提交记录

### 成绩接口

- `GET /api/v1/grades/my` - 学生查询自己成绩
- `GET /api/v1/grades/class/{class_id}` - 教师查询班级成绩
- `GET /api/v1/grades/export/{assignment_id}` - 导出作业成绩表

## 权限说明

- **student**: 只能访问自己的课程、作业、提交、成绩
- **teacher**: 只能管理自己的课程、班级、作业、学生
- **admin**: 全平台管理

## 开发环境要求

- Python 3.8+
- MySQL 8.0+
- Redis 6.0+ (可选，用于缓存和消息队列)

## 注意事项

1. 生产环境请修改 `SECRET_KEY` 为安全的随机字符串
2. 建议使用 HTTPS 协议
3. 数据库连接池配置已优化，适合轻量级部署（512MB内存限制）
4. 作业发布后不可修改题目ID

## 许可证

MIT License
