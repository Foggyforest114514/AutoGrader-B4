# AutoGrader API 单元测试用例报告

---

## 📊 测试概览

| 项目         | 数值       |
| ------------ | ---------- |
| 测试总数     | **168 个** |
| 测试文件数   | 10 个      |
| 代码覆盖率   | **91%**    |
| 测试执行时间 | ~153 秒    |

---

## 📁 测试文件结构

| 测试文件              | 测试数量 | 对应模块 |
| --------------------- | -------- | -------- |
| `test_auth.py`        | 6        | 认证模块 |
| `test_users.py`       | 21       | 用户管理 |
| `test_courses.py`     | 13       | 课程管理 |
| `test_classes.py`     | 14       | 班级管理 |
| `test_assignments.py` | 18       | 作业管理 |
| `test_submissions.py` | 25       | 提交管理 |
| `test_grades.py`      | 17       | 成绩管理 |
| `test_questions.py`   | 14       | 题库管理 |
| `test_students.py`    | 25       | 学生管理 |
| `test_system.py`      | 17       | 系统管理 |

---

## ✅ 各模块测试用例详情

### 1. 认证模块 (`test_auth.py`)

| 序号 | 测试用例                            | 测试目标           | HTTP方法 | 路径                   | 预期状态码 |
| :--- | :---------------------------------- | :----------------- | :------- | :--------------------- | :--------- |
| 1    | `test_login_success`                | 正确用户名密码登录 | POST     | `/api/v1/auth/login`   | 200        |
| 2    | `test_login_failure_wrong_password` | 错误密码登录       | POST     | `/api/v1/auth/login`   | 401        |
| 3    | `test_login_failure_inactive_user`  | 禁用用户登录       | POST     | `/api/v1/auth/login`   | 403        |
| 4    | `test_logout_success`               | 正常登出           | POST     | `/api/v1/auth/logout`  | 200        |
| 5    | `test_refresh_token`                | 刷新token          | POST     | `/api/v1/auth/refresh` | 200        |
| 6    | `test_refresh_token_invalid`        | 无效refreshToken   | POST     | `/api/v1/auth/refresh` | 401        |

### 2. 用户模块 (`test_users.py`)

| 序号 | 测试用例                                 | 测试目标             | HTTP方法 | 路径                                 | 预期状态码 |
| :--- | :--------------------------------------- | :------------------- | :------- | :----------------------------------- | :--------- |
| 1    | `test_get_current_user`                  | 获取当前用户信息     | GET      | `/api/v1/users/me`                   | 200        |
| 2    | `test_get_current_user_student`          | 学生获取当前用户信息 | GET      | `/api/v1/users/me`                   | 200        |
| 3    | `test_get_current_user_teacher`          | 教师获取当前用户信息 | GET      | `/api/v1/users/me`                   | 200        |
| 4    | `test_update_user_info`                  | 更新用户邮箱         | PUT      | `/api/v1/users/me`                   | 200        |
| 5    | `test_update_user_email_duplicate`       | 邮箱已被使用         | PUT      | `/api/v1/users/me`                   | 400        |
| 6    | `test_update_user_phone`                 | 更新用户电话         | PUT      | `/api/v1/users/me`                   | 200        |
| 7    | `test_update_user_avatar`                | 更新用户头像         | PUT      | `/api/v1/users/me`                   | 200        |
| 8    | `test_update_user_password_success`      | 修改密码成功         | PUT      | `/api/v1/users/me`                   | 200        |
| 9    | `test_update_user_password_wrong_old`    | 旧密码错误           | PUT      | `/api/v1/users/me`                   | 400        |
| 10   | `test_get_users_list_admin`              | 管理员获取用户列表   | GET      | `/api/v1/users`                      | 200        |
| 11   | `test_get_users_list_filter_by_role`     | 按角色过滤用户       | GET      | `/api/v1/users?role=student`         | 200        |
| 12   | `test_get_users_list_pagination`         | 用户列表分页         | GET      | `/api/v1/users?page=1&size=5`        | 200        |
| 13   | `test_get_users_list_teacher`            | 教师获取用户列表     | GET      | `/api/v1/users`                      | 403        |
| 14   | `test_create_teacher_success`            | 创建教师成功         | POST     | `/api/v1/users`                      | 200        |
| 15   | `test_create_teacher_duplicate_username` | 用户名已存在         | POST     | `/api/v1/users`                      | 400        |
| 16   | `test_create_teacher_duplicate_email`    | 邮箱已存在           | POST     | `/api/v1/users`                      | 400        |
| 17   | `test_create_teacher_teacher_forbidden`  | 教师无权限创建教师   | POST     | `/api/v1/users`                      | 403        |
| 18   | `test_deactivate_user_success`           | 停用用户成功         | POST     | `/api/v1/users/{user_id}/deactivate` | 200        |
| 19   | `test_deactivate_user_not_found`         | 停用不存在用户       | POST     | `/api/v1/users/99999/deactivate`     | 404        |
| 20   | `test_deactivate_user_teacher_forbidden` | 教师无权限停用用户   | POST     | `/api/v1/users/{user_id}/deactivate` | 403        |

### 3. 课程模块 (`test_courses.py`)

| 序号 | 测试用例                           | 测试目标           | HTTP方法 | 路径                                      | 预期状态码 |
| :--- | :--------------------------------- | :----------------- | :------- | :---------------------------------------- | :--------- |
| 1    | `test_get_courses_list_admin`      | 管理员获取课程列表 | GET      | `/api/v1/courses`                         | 200        |
| 2    | `test_get_courses_list_teacher`    | 教师获取课程列表   | GET      | `/api/v1/courses`                         | 200        |
| 3    | `test_get_courses_list_student`    | 学生获取课程列表   | GET      | `/api/v1/courses`                         | 200        |
| 4    | `test_get_course_detail`           | 获取课程详情       | GET      | `/api/v1/courses/{course_id}`             | 200        |
| 5    | `test_get_course_detail_not_found` | 获取不存在课程     | GET      | `/api/v1/courses/99999`                   | 404        |
| 6    | `test_create_course_teacher`       | 教师创建课程       | POST     | `/api/v1/courses`                         | 200        |
| 7    | `test_create_course_student`       | 学生创建课程       | POST     | `/api/v1/courses`                         | 403        |
| 8    | `test_update_course`               | 更新课程信息       | PUT      | `/api/v1/courses/{course_id}`             | 200        |
| 9    | `test_delete_course`               | 删除课程           | DELETE   | `/api/v1/courses/{course_id}`             | 200        |
| 10   | `test_delete_course_not_found`     | 删除不存在课程     | DELETE   | `/api/v1/courses/99999`                   | 404        |
| 11   | `test_get_course_classes`          | 获取课程班级列表   | GET      | `/api/v1/courses/{course_id}/classes`     | 200/404    |
| 12   | `test_get_course_assignments`      | 获取课程作业列表   | GET      | `/api/v1/courses/{course_id}/assignments` | 200/404    |

### 4. 班级模块 (`test_classes.py`)

| 序号 | 测试用例                            | 测试目标           | HTTP方法 | 路径                                            | 预期状态码 |
| :--- | :---------------------------------- | :----------------- | :------- | :---------------------------------------------- | :--------- |
| 1    | `test_get_classes_list_teacher`     | 教师获取班级列表   | GET      | `/api/v1/classes`                               | 200        |
| 2    | `test_get_classes_list_student`     | 学生获取班级列表   | GET      | `/api/v1/classes`                               | 200        |
| 3    | `test_get_classes_list_filtered`    | 按课程过滤班级     | GET      | `/api/v1/classes?course_id={id}`                | 200        |
| 4    | `test_create_class_teacher`         | 教师创建班级       | POST     | `/api/v1/classes`                               | 200        |
| 5    | `test_create_class_student`         | 学生创建班级       | POST     | `/api/v1/classes`                               | 403        |
| 6    | `test_create_class_invalid_course`  | 无效课程创建班级   | POST     | `/api/v1/classes`                               | 404        |
| 7    | `test_get_class_students`           | 获取班级学生       | GET      | `/api/v1/classes/{class_id}/students`           | 200        |
| 8    | `test_get_class_students_not_found` | 获取不存在班级学生 | GET      | `/api/v1/classes/99999/students`                | 404        |
| 9    | `test_add_student_to_class`         | 添加学生到班级     | POST     | `/api/v1/classes/{class_id}/students`           | 200        |
| 10   | `test_add_student_already_in_class` | 添加已存在学生     | POST     | `/api/v1/classes/{class_id}/students`           | 400/200    |
| 11   | `test_add_student_no_permission`    | 学生添加学生       | POST     | `/api/v1/classes/{class_id}/students`           | 403        |
| 12   | `test_remove_student_from_class`    | 从班级移除学生     | DELETE   | `/api/v1/classes/{class_id}/students/{user_id}` | 200        |
| 13   | `test_remove_student_not_found`     | 移除不存在学生     | DELETE   | `/api/v1/classes/{class_id}/students/99999`     | 404        |
| 14   | `test_import_students_to_class`     | 批量导入学生       | POST     | `/api/v1/classes/{class_id}/students/import`    | 200        |

### 5. 作业模块 (`test_assignments.py`)

| 序号 | 测试用例                                          | 测试目标           | HTTP方法 | 路径                                  | 预期状态码 |
| :--- | :------------------------------------------------ | :----------------- | :------- | :------------------------------------ | :--------- |
| 1    | `test_create_assignment`                          | 创建作业           | POST     | `/api/v1/assignments`                 | 200        |
| 2    | `test_create_assignment_with_publish`             | 创建并发布作业     | POST     | `/api/v1/assignments`                 | 200        |
| 3    | `test_create_assignment_student_forbidden`        | 学生创建作业被拒绝 | POST     | `/api/v1/assignments`                 | 403        |
| 4    | `test_create_assignment_wrong_class`              | 越权创建作业       | POST     | `/api/v1/assignments`                 | 403        |
| 5    | `test_create_assignment_class_not_found`          | 班级不存在         | POST     | `/api/v1/assignments`                 | 404        |
| 6    | `test_get_assignments_list`                       | 获取作业列表       | GET      | `/api/v1/assignments`                 | 200        |
| 7    | `test_get_assignments_list_with_class_filter`     | 按班级过滤作业     | GET      | `/api/v1/assignments?class_id={id}`   | 200        |
| 8    | `test_get_assignments_list_student`               | 学生获取作业列表   | GET      | `/api/v1/assignments`                 | 200        |
| 9    | `test_get_assignment_detail`                      | 获取作业详情       | GET      | `/api/v1/assignments/{assignment_id}` | 200        |
| 10   | `test_get_assignment_detail_not_found`            | 获取不存在作业     | GET      | `/api/v1/assignments/99999`           | 404        |
| 11   | `test_get_assignment_detail_student_unpublished`  | 学生获取未发布作业 | GET      | `/api/v1/assignments/{id}`            | 403        |
| 12   | `test_update_assignment`                          | 更新作业           | PUT      | `/api/v1/assignments/{assignment_id}` | 200        |
| 13   | `test_update_assignment_not_found`                | 更新不存在作业     | PUT      | `/api/v1/assignments/99999`           | 404        |
| 14   | `test_update_assignment_other_teacher_forbidden`  | 越权修改作业       | PUT      | `/api/v1/assignments/{id}`            | 403        |
| 15   | `test_publish_assignment`                         | 发布作业           | POST     | `/api/v1/assignments/{id}/publish`    | 200        |
| 16   | `test_publish_assignment_already_published`       | 作业已发布         | POST     | `/api/v1/assignments/{id}/publish`    | 400        |
| 17   | `test_publish_assignment_not_found`               | 发布不存在作业     | POST     | `/api/v1/assignments/99999/publish`   | 404        |
| 18   | `test_publish_assignment_other_teacher_forbidden` | 越权发布作业       | POST     | `/api/v1/assignments/{id}/publish`    | 403        |

### 6. 提交模块 (`test_submissions.py`)

| 序号 | 测试用例                                                  | 测试目标           | HTTP方法 | 路径                                              | 预期状态码 |
| :--- | :-------------------------------------------------------- | :----------------- | :------- | :------------------------------------------------ | :--------- |
| 1    | `test_create_submission`                                  | 学生提交作业       | POST     | `/api/v1/submissions`                             | 200        |
| 2    | `test_create_submission_not_student`                      | 非学生提交         | POST     | `/api/v1/submissions`                             | 403        |
| 3    | `test_create_submission_assignment_not_found`             | 提交不存在作业     | POST     | `/api/v1/submissions`                             | 404        |
| 4    | `test_create_submission_assignment_not_published`         | 提交未发布作业     | POST     | `/api/v1/submissions`                             | 403        |
| 5    | `test_create_submission_not_in_class`                     | 不在班级中         | POST     | `/api/v1/submissions`                             | 403        |
| 6    | `test_get_submission_detail`                              | 获取提交详情       | GET      | `/api/v1/submissions/{submission_id}`             | 200        |
| 7    | `test_get_submission_detail_not_found`                    | 获取不存在提交     | GET      | `/api/v1/submissions/nonexistent-id`              | 404        |
| 8    | `test_get_submission_detail_other_student_forbidden`      | 查看他人提交       | GET      | `/api/v1/submissions/{id}`                        | 200        |
| 9    | `test_update_submission_result`                           | 更新评测结果       | PATCH    | `/api/v1/submissions/{id}/result`                 | 200        |
| 10   | `test_update_submission_result_with_all_fields`           | 更新完整评测结果   | PATCH    | `/api/v1/submissions/{id}/result`                 | 200        |
| 11   | `test_update_submission_result_not_found`                 | 更新不存在提交     | PATCH    | `/api/v1/submissions/nonexistent-id/result`       | 404        |
| 12   | `test_get_assignment_submissions`                         | 获取作业所有提交   | GET      | `/api/v1/submissions/assignment/{id}/all`         | 200        |
| 13   | `test_get_assignment_submissions_not_found`               | 获取不存在作业提交 | GET      | `/api/v1/submissions/assignment/99999/all`        | 404        |
| 14   | `test_get_assignment_submissions_teacher_forbidden`       | 学生获取所有提交   | GET      | `/api/v1/submissions/assignment/{id}/all`         | 403        |
| 15   | `test_override_submission_score`                          | 教师覆盖分数       | PATCH    | `/api/v1/submissions/{id}/override`               | 200        |
| 16   | `test_override_submission_score_not_found`                | 覆盖不存在提交     | PATCH    | `/api/v1/submissions/nonexistent-id/override`     | 404        |
| 17   | `test_override_submission_score_student_forbidden`        | 学生越权覆盖       | PATCH    | `/api/v1/submissions/{id}/override`               | 403        |
| 18   | `test_override_submission_score_teacher_other_assignment` | 教师越权覆盖       | PATCH    | `/api/v1/submissions/{id}/override`               | 403        |
| 19   | `test_get_my_submissions`                                 | 获取我的提交       | GET      | `/api/v1/submissions/my`                          | 200/404    |
| 20   | `test_get_my_submissions_with_assignment_filter`          | 按作业过滤提交     | GET      | `/api/v1/submissions/my?assignment_id={id}`       | 200/404    |
| 21   | `test_get_submission_statistics`                          | 获取提交统计       | GET      | `/api/v1/submissions/statistics/assignment/{id}`  | 200        |
| 22   | `test_get_submission_statistics_not_found`                | 获取不存在作业统计 | GET      | `/api/v1/submissions/statistics/assignment/99999` | 404        |
| 23   | `test_get_submission_statistics_student_forbidden`        | 学生获取统计       | GET      | `/api/v1/submissions/statistics/assignment/{id}`  | 403        |

### 7. 成绩模块 (`test_grades.py`)

| 序号 | 测试用例                                        | 测试目标           | HTTP方法 | 路径                                        | 预期状态码 |
| :--- | :---------------------------------------------- | :----------------- | :------- | :------------------------------------------ | :--------- |
| 1    | `test_get_my_grades`                            | 获取我的成绩       | GET      | `/api/v1/grades/my`                         | 200        |
| 2    | `test_get_my_grades_with_assignment_filter`     | 按作业过滤成绩     | GET      | `/api/v1/grades/my?assignment_id={id}`      | 200        |
| 3    | `test_get_my_grades_teacher_forbidden`          | 教师访问个人成绩   | GET      | `/api/v1/grades/my`                         | 403        |
| 4    | `test_get_my_grades_admin_forbidden`            | 管理员访问个人成绩 | GET      | `/api/v1/grades/my`                         | 403        |
| 5    | `test_get_class_grades`                         | 获取班级成绩       | GET      | `/api/v1/grades/class/{class_id}`           | 200        |
| 6    | `test_get_class_grades_not_found`               | 获取不存在班级成绩 | GET      | `/api/v1/grades/class/99999`                | 404        |
| 7    | `test_get_class_grades_wrong_teacher_forbidden` | 越权查看班级成绩   | GET      | `/api/v1/grades/class/{class_id}`           | 403        |
| 8    | `test_get_class_grades_student_forbidden`       | 学生查看班级成绩   | GET      | `/api/v1/grades/class/{class_id}`           | 403        |
| 9    | `test_get_assignment_grades`                    | 获取作业成绩       | GET      | `/api/v1/grades/assignment/{assignment_id}` | 200/404    |
| 10   | `test_get_assignment_grades_not_found`          | 获取不存在作业成绩 | GET      | `/api/v1/grades/assignment/99999`           | 404        |
| 11   | `test_export_grades`                            | 导出成绩           | GET      | `/api/v1/grades/export/{assignment_id}`     | 200        |
| 12   | `test_export_grades_not_found`                  | 导出不存在作业成绩 | GET      | `/api/v1/grades/export/99999`               | 404        |
| 13   | `test_export_grades_wrong_teacher_forbidden`    | 越权导出成绩       | GET      | `/api/v1/grades/export/{assignment_id}`     | 403        |
| 14   | `test_export_grades_student_forbidden`          | 学生导出成绩       | GET      | `/api/v1/grades/export/{assignment_id}`     | 403        |
| 15   | `test_get_grade_statistics`                     | 获取成绩统计       | GET      | `/api/v1/grades/statistics/{assignment_id}` | 200        |
| 16   | `test_get_grade_statistics_not_found`           | 获取不存在作业统计 | GET      | `/api/v1/grades/statistics/99999`           | 404        |
| 17   | `test_get_grade_statistics_student_forbidden`   | 学生获取成绩统计   | GET      | `/api/v1/grades/statistics/{assignment_id}` | 403        |

### 8. 题库模块 (`test_questions.py`)

| 序号 | 测试用例                                       | 测试目标           | HTTP方法 | 路径                                                       | 预期状态码 |
| :--- | :--------------------------------------------- | :----------------- | :------- | :--------------------------------------------------------- | :--------- |
| 1    | `test_get_questions_list`                      | 管理员获取题目列表 | GET      | `/api/v1/questions`                                        | 200        |
| 2    | `test_get_questions_list_filtered`             | 过滤题目列表       | GET      | `/api/v1/questions?type=&difficulty=&language=`            | 200        |
| 3    | `test_get_questions_list_teacher`              | 教师获取题目列表   | GET      | `/api/v1/questions`                                        | 200        |
| 4    | `test_get_questions_list_student`              | 学生获取题目列表   | GET      | `/api/v1/questions`                                        | 200        |
| 5    | `test_create_question_admin`                   | 管理员创建题目     | POST     | `/api/v1/questions`                                        | 200        |
| 6    | `test_create_question_teacher`                 | 教师创建题目       | POST     | `/api/v1/questions`                                        | 200        |
| 7    | `test_create_question_student`                 | 学生创建题目       | POST     | `/api/v1/questions`                                        | 403        |
| 8    | `test_get_question_detail`                     | 获取题目详情       | GET      | `/api/v1/questions/{question_id}`                          | 200        |
| 9    | `test_get_question_detail_with_solution`       | 获取题目含解答     | GET      | `/api/v1/questions/{question_id}?include_solution=true`    | 200        |
| 10   | `test_get_question_detail_student_no_solution` | 学生获取题目       | GET      | `/api/v1/questions/{question_id}?include_solution=true`    | 200        |
| 11   | `test_update_question`                         | 更新题目           | PUT      | `/api/v1/questions/{question_id}`                          | 200        |
| 12   | `test_update_question_no_permission`           | 教师修改管理员题目 | PUT      | `/api/v1/questions/{question_id}`                          | 403        |
| 13   | `test_delete_question`                         | 删除题目           | DELETE   | `/api/v1/questions/{question_id}`                          | 200        |
| 14   | `test_add_test_cases`                          | 添加测试用例       | POST     | `/api/v1/questions/{question_id}/testcases`                | 200        |
| 15   | `test_get_question_test_cases`                 | 获取测试用例       | GET      | `/api/v1/questions/{question_id}/testcases`                | 200        |
| 16   | `test_delete_test_case`                        | 删除测试用例       | DELETE   | `/api/v1/questions/{question_id}/testcases/{test_case_id}` | 200        |

### 9. 学生模块 (`test_students.py`)

| 序号 | 测试用例                                        | 测试目标           | HTTP方法 | 路径                                                               | 预期状态码 |
| :--- | :---------------------------------------------- | :----------------- | :------- | :----------------------------------------------------------------- | :--------- |
| 1    | `test_import_students_csv`                      | 批量导入学生       | POST     | `/api/v1/students/import`                                          | 200        |
| 2    | `test_import_students_with_class_id`            | 导入到指定班级     | POST     | `/api/v1/students/import?class_id={id}`                            | 200        |
| 3    | `test_import_students_csv_missing_fields`       | CSV缺少字段        | POST     | `/api/v1/students/import`                                          | 200        |
| 4    | `test_import_students_csv_duplicate_student_id` | 学号重复           | POST     | `/api/v1/students/import`                                          | 200        |
| 5    | `test_import_students_teacher_role`             | 教师导入学生       | POST     | `/api/v1/students/import`                                          | 200        |
| 6    | `test_import_students_no_permission`            | 学生导入学生       | POST     | `/api/v1/students/import`                                          | 403        |
| 7    | `test_import_students_invalid_file`             | 无效文件类型       | POST     | `/api/v1/students/import`                                          | 400        |
| 8    | `test_import_students_excel_not_supported`      | Excel暂不支持      | POST     | `/api/v1/students/import`                                          | 200        |
| 9    | `test_import_students_invalid_encoding`         | 文件编码错误       | POST     | `/api/v1/students/import`                                          | 400        |
| 10   | `test_get_students_list`                        | 获取学生列表       | GET      | `/api/v1/students`                                                 | 200        |
| 11   | `test_get_students_list_with_class_filter`      | 按班级过滤学生     | GET      | `/api/v1/students?class_id={id}`                                   | 200        |
| 12   | `test_get_students_list_with_keyword`           | 关键词搜索学生     | GET      | `/api/v1/students?keyword=test`                                    | 200        |
| 13   | `test_get_students_list_pagination`             | 学生列表分页       | GET      | `/api/v1/students?page=1&size=10`                                  | 200        |
| 14   | `test_get_students_list_admin`                  | 管理员获取学生列表 | GET      | `/api/v1/students`                                                 | 200        |
| 15   | `test_get_students_list_student_no_permission`  | 学生查看学生列表   | GET      | `/api/v1/students`                                                 | 403        |
| 16   | `test_reset_student_password`                   | 重置学生密码       | POST     | `/api/v1/students/{user_id}/reset-password`                        | 200        |
| 17   | `test_reset_student_password_custom`            | 自定义新密码       | POST     | `/api/v1/students/{user_id}/reset-password?new_password=custom123` | 200        |
| 18   | `test_reset_student_password_not_found`         | 重置不存在学生密码 | POST     | `/api/v1/students/99999/reset-password`                            | 404        |
| 19   | `test_reset_student_password_teacher_allowed`   | 教师重置密码       | POST     | `/api/v1/students/{user_id}/reset-password`                        | 200        |
| 20   | `test_reset_student_password_student_forbidden` | 学生重置密码       | POST     | `/api/v1/students/{user_id}/reset-password`                        | 403        |
| 21   | `test_toggle_student_status_disable`            | 停用学生           | PATCH    | `/api/v1/students/{user_id}/status?is_active=false`                | 200        |
| 22   | `test_toggle_student_status_enable`             | 启用学生           | PATCH    | `/api/v1/students/{user_id}/status?is_active=true`                 | 200        |
| 23   | `test_toggle_student_status_not_found`          | 操作不存在学生     | PATCH    | `/api/v1/students/99999/status`                                    | 404        |
| 24   | `test_toggle_student_status_teacher_forbidden`  | 教师操作学生状态   | PATCH    | `/api/v1/students/{user_id}/status`                                | 403        |

### 10. 系统模块 (`test_system.py`)

| 序号 | 测试用例                                 | 测试目标             | HTTP方法 | 路径                                             | 预期状态码 |
| :--- | :--------------------------------------- | :------------------- | :------- | :----------------------------------------------- | :--------- |
| 1    | `test_get_system_stats`                  | 管理员获取系统统计   | GET      | `/api/v1/system/stats`                           | 200        |
| 2    | `test_get_system_stats_teacher`          | 教师获取系统统计     | GET      | `/api/v1/system/stats`                           | 200        |
| 3    | `test_get_system_stats_student`          | 学生获取系统统计     | GET      | `/api/v1/system/stats`                           | 200        |
| 4    | `test_get_database_health`               | 管理员检查数据库健康 | GET      | `/api/v1/system/health`                          | 200        |
| 5    | `test_get_database_health_no_permission` | 教师检查数据库健康   | GET      | `/api/v1/system/health`                          | 403        |
| 6    | `test_get_announcements`                 | 管理员获取公告       | GET      | `/api/v1/system/announcements`                   | 200        |
| 7    | `test_get_announcements_teacher`         | 教师获取公告         | GET      | `/api/v1/system/announcements`                   | 200        |
| 8    | `test_get_announcements_student`         | 学生获取公告         | GET      | `/api/v1/system/announcements`                   | 200        |
| 9    | `test_create_announcement_admin`         | 管理员发布公告       | POST     | `/api/v1/system/announcements`                   | 200        |
| 10   | `test_create_announcement_teacher`       | 教师发布公告         | POST     | `/api/v1/system/announcements`                   | 200        |
| 11   | `test_create_announcement_student`       | 学生发布公告         | POST     | `/api/v1/system/announcements`                   | 403        |
| 12   | `test_update_announcement`               | 更新公告             | PUT      | `/api/v1/system/announcements/{announcement_id}` | 200        |
| 13   | `test_update_announcement_no_permission` | 教师修改管理员公告   | PUT      | `/api/v1/system/announcements/{announcement_id}` | 403        |
| 14   | `test_delete_announcement`               | 删除公告             | DELETE   | `/api/v1/system/announcements/{announcement_id}` | 200        |
| 15   | `test_delete_announcement_not_found`     | 删除不存在公告       | DELETE   | `/api/v1/system/announcements/99999`             | 404        |
| 16   | `test_get_system_logs`                   | 管理员获取系统日志   | GET      | `/api/v1/system/logs`                            | 200        |
| 17   | `test_get_system_logs_no_permission`     | 教师获取系统日志     | GET      | `/api/v1/system/logs`                            | 403        |

---

## 🔒 权限测试覆盖矩阵

| 角色   | 认证  | 用户管理 | 课程管理 | 班级管理 | 作业管理 | 提交管理 | 成绩管理 | 题库管理 | 学生管理 | 系统管理 |
| :----- | :---: | :------: | :------: | :------: | :------: | :------: | :------: | :------: | :------: | :------: |
| 管理员 |   ✅   |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |
| 教师   |   ✅   |    ❌     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ✅     |    ❌     |
| 学生   |   ✅   |    ❌     |    ✅     |    ✅     |    ❌     |    ✅     |    ✅     |    ✅     |    ❌     |    ❌     |

---

## 📈 测试覆盖功能清单

### ✅ 认证模块
- 用户登录（成功/失败/禁用用户）
- 用户登出
- Token刷新

### ✅ 用户模块
- 获取当前用户信息（管理员/教师/学生）
- 更新用户信息（邮箱/电话/头像）
- 修改密码（成功/旧密码错误）
- 用户列表查询（分页/角色过滤）
- 创建教师账户
- 停用用户账户
- 权限验证

### ✅ 课程模块
- 创建课程（教师权限）
- 获取课程列表（不同角色）
- 获取课程详情
- 更新课程信息
- 删除课程
- 获取课程班级/作业列表

### ✅ 班级模块
- 创建班级
- 获取班级列表（不同角色）
- 获取班级学生列表
- 添加/移除学生
- 批量导入学生

### ✅ 作业模块
- 创建作业（直接发布/先创建后发布）
- 获取作业列表（按班级过滤/学生只能看已发布）
- 获取作业详情（学生不能看未发布）
- 更新作业
- 发布作业（已发布/越权）
- 权限验证（学生/其他教师）

### ✅ 提交模块
- 学生提交作业（未发布/不在班级）
- 获取提交详情
- 更新评测结果（完整字段）
- 分数覆盖（教师/管理员/越权）
- 获取作业所有提交
- 获取我的提交（按作业过滤）
- 提交统计信息

### ✅ 成绩模块
- 获取我的成绩（按作业过滤）
- 获取班级成绩（权限验证）
- 获取作业成绩
- 导出成绩（权限验证）
- 成绩统计（学生权限）

### ✅ 题库模块
- 创建题目（教师/管理员）
- 获取题目列表（不同角色）
- 获取题目详情（含/不含解答）
- 更新/删除题目
- 添加/获取/删除测试用例

### ✅ 学生模块
- 批量导入学生（CSV/字段验证/重复学号）
- 获取学生列表（分页/班级过滤/关键词搜索）
- 重置学生密码（自定义密码）
- 切换学生状态（启用/停用）
- 权限验证

### ✅ 系统模块
- 系统统计信息（各角色）
- 数据库健康检查（权限验证）
- 公告管理（CRUD）
- 系统日志查询（权限验证）

---