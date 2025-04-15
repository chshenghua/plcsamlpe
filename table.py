from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import sys
# 创建基类
Base = declarative_base()

# 定义数据模型
class StudentScore(Base):
    __tablename__ = 'student_scores'  # 数据库表名
    
    id = Column(Integer, primary_key=True, comment='编号')
    name = Column(String(20), nullable=False, comment='姓名')
    chinese = Column(Integer, comment='语文')
    math = Column(Integer, comment='数学')
    physics = Column(Integer, comment='物理')
    chemistry = Column(Integer, comment='化学')

    def __repr__(self):
        return f"<Student {self.name}>"

# 初始化数据库连接
engine = create_engine('sqlite:///student.db', echo=False)
Base.metadata.create_all(engine)

# 创建会话工厂
Session = sessionmaker(bind=engine)
session = Session()

# 添加初始数据
def init_data():
    students = [
        StudentScore(name='张三', chinese=85, math=90, physics=88, chemistry=92),
        StudentScore(name='李四', chinese=78, math=85, physics=80, chemistry=85),
        StudentScore(name='王五', chinese=92, math=88, physics=85, chemistry=90),
        StudentScore(name='赵六', chinese=65, math=70, physics=75, chemistry=68),
        StudentScore(name='陈七', chinese=88, math=92, physics=90, chemistry=94),
        StudentScore(name='杨八', chinese=73, math=68, physics=72, chemistry=70),
        StudentScore(name='周九', chinese=95, math=89, physics=91, chemistry=93),
        StudentScore(name='吴十', chinese=81, math=77, physics=79, chemistry=83),
        StudentScore(name='郑十一', chinese=69, math=73, physics=68, chemistry=71),
        StudentScore(name='孙十二', chinese=87, math=84, physics=86, chemistry=89)
    ]
    session.add_all(students)
    session.commit()

# 查询所有学生
def show_all():
    students = session.query(StudentScore).order_by(StudentScore.id).all()
    print("\n当前所有学生成绩：")
    print("{:<5}{:<8}{:<6}{:<6}{:<6}{:<6}".format(
        "ID", "姓名", "语文", "数学", "物理", "化学"))
    for s in students:
        print("{:<5}{:<8}{:<6}{:<6}{:<6}{:<6}".format(
            s.id, s.name, s.chinese, s.math, s.physics, s.chemistry))

# 添加新学生
def add_student():
    print("\n添加新学生：")
    name = input("姓名：")
    chinese = int(input("语文："))
    math = int(input("数学："))
    physics = int(input("物理："))
    chemistry = int(input("化学："))
    
    new_student = StudentScore(
        name=name,
        chinese=chinese,
        math=math,
        physics=physics,
        chemistry=chemistry
    )
    session.add(new_student)
    session.commit()
    print("添加成功！")

# 删除学生
def delete_student():
    student_id = int(input("\n请输入要删除的学生ID："))
    student = session.query(StudentScore).get(student_id)
    if student:
        session.delete(student)
        session.commit()
        print(f"已删除ID为 {student_id} 的学生")
    else:
        print("未找到该学生")

def main():
    """主程序"""
    # 初始化数据库连接
    engine = create_engine('sqlite:///student.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        while True:
            try:
                print("\n学生成绩管理系统")
                print("1. 显示所有记录")
                print("2. 添加新记录")
                print("3. 删除记录")
                print("4. 退出")
                
                choice = input("\n请选择操作(1-4): ").strip()
                
                if choice == '1':
                    show_all(session)
                elif choice == '2':
                    add_student(session)
                elif choice == '3':
                    delete_student(session)
                elif choice == '4':
                    raise KeyboardInterrupt  # 触发退出
                else:
                    print("无效的选择，请重新输入")
                    
            except ValueError as e:
                print(f"输入错误: {e}")
            except Exception as e:
                print(f"发生错误: {e}")
                
    except KeyboardInterrupt:
        print("\n正在退出程序...")
    finally:
        print("正在关闭数据库连接...")
        session.close()
        print("程序已退出！")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序异常退出: {e}")
        sys.exit(1)
