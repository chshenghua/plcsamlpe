#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import sys

# 创建基类
Base = declarative_base()

class StudentScore(Base):
    """学生成绩表"""
    __tablename__ = 'student_scores'
    
    id = Column(Integer, primary_key=True, comment='编号')
    name = Column(String(20), nullable=False, comment='姓名')
    chinese = Column(Integer, comment='语文')
    math = Column(Integer, comment='数学')
    physics = Column(Integer, comment='物理')
    chemistry = Column(Integer, comment='化学')

    def __repr__(self):
        return f"<Student {self.name}>"

    @property
    def average(self):
        """计算平均分"""
        scores = [self.chinese, self.math, self.physics, self.chemistry]
        return sum(scores) / len(scores)

def validate_score(score_str: str) -> int:
    """验证分数输入"""
    try:
        score = int(score_str)
        if 0 <= score <= 100:
            return score
        raise ValueError("分数必须在0-100之间")
    except ValueError:
        raise ValueError("请输入有效的分数")

def get_valid_input(prompt: str, validator=None) -> str:
    """获取并验证用户输入"""
    while True:
        try:
            value = input(prompt).strip()
            if validator:
                value = validator(value)
            return value
        except ValueError as e:
            print(f"输入错误: {e}")

def add_student(session):
    """添加新学生记录"""
    try:
        name = get_valid_input("姓名：")
        if not name:
            print("姓名不能为空")
            return
            
        chinese = get_valid_input("语文分数：", validate_score)
        math = get_valid_input("数学分数：", validate_score)
        physics = get_valid_input("物理分数：", validate_score)
        chemistry = get_valid_input("化学分数：", validate_score)
        
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
    except Exception as e:
        print(f"添加失败: {e}")
        session.rollback()

def show_all(session):
    """显示所有学生记录"""
    try:
        students = session.query(StudentScore).order_by(StudentScore.id).all()
        if not students:
            print("\n暂无学生记录")
            return
            
        print("\n当前所有学生成绩：")
        header = "  ID    姓名     语文  数学  物理  化学  平均分"
        print(header)
        print("-" * len(header))
        
        for s in students:
            print("{:^5} {:^8} {:^5} {:^5} {:^5} {:^5} {:^6.1f}".format(
                s.id, s.name, s.chinese, s.math, s.physics, s.chemistry, s.average))
                
        print("-" * len(header))
            
    except Exception as e:
        print(f"查询失败: {e}")

def reset_sequence(session):
    """重置主键序列"""
    try:
        session.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM student_scores) WHERE name = 'student_scores'")
        session.commit()
    except Exception as e:
        print(f"重置序列失败: {e}")
        session.rollback()

def delete_student(session):
    """删除学生记录"""
    try:
        student_id = get_valid_input("请输入要删除的学生ID：", int)
        student = session.query(StudentScore).get(student_id)
        if student:
            session.delete(student)
            session.commit()
            # 只重置序列，不修改现有记录
            reset_sequence(session)
            print(f"已删除ID为 {student_id} 的学生")
        else:
            print("未找到该学生")
    except Exception as e:
        print(f"删除失败: {e}")
        session.rollback()

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
