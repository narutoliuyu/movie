from app import create_app
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 检查是否有用户
    users = User.query.all()
    print(f"数据库中的用户数量: {len(users)}")
    
    for user in users:
        print(f"用户ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
    
    # 如果没有用户，创建一个测试用户
    if not users:
        print("创建测试用户 'admin'...")
        test_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"测试用户已创建，ID: {test_user.id}") 