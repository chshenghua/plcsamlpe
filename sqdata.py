#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Float
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

    @property
    def average(self):
        """计算平均分"""
        scores = [self.chinese, self.math, self.physics, self.chemistry]
        return sum(scores) / len(scores)

    def __repr__(self):
        return f"<Student {self.name}>"

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
            if not value:
                raise ValueError("输入不能为空")
            if validator:
                value = validator(value)
            return value
        except ValueError as e:
            print(f"输入错误: {e}")

def show_all():
    """显示所有学生记录"""
    try:
        students = session.query(StudentScore).order_by(StudentScore.id).all()
        if not students:
            print("\n暂无学生记录\n")
            return
            
        print("\n当前所有学生成绩：")
        print("=" * 60)
        print("ID    姓名     语文  数学  物理  化学  平均分")
        print("-" * 60)
        
        for s in students:
            avg = s.average
            if avg >= 90:
                symbol = "★"  # 优秀
            elif avg >= 80:
                symbol = "☆"  # 良好
            else:
                symbol = " "  # 普通
                
            print("{:2d}  {:^8} {:4d}  {:4d}  {:4d}  {:4d}  {:5.1f} {}".format(
                s.id, s.name, s.chinese, s.math, s.physics, s.chemistry, avg, symbol))
                
        print("-" * 60)
        
        # 计算班级平均分
        total = len(students)
        total_avg = sum(s.average for s in students) / total
        print(f"班级平均分: {total_avg:.1f}")
        print("=" * 60)
        
        # 添加图例说明
        print("\n成绩等级：")
        print("★ - 优秀（90分以上）")
        print("☆ - 良好（80-89分）")
        
    except Exception as e:
        print(f"查询失败: {e}")

def add_student():
    """添加新学生"""
    try:
        print("\n添加新学生：")
        name = get_valid_input("姓名：")
        chinese = get_valid_input("语文成绩：", validate_score)
        math = get_valid_input("数学成绩：", validate_score)
        physics = get_valid_input("物理成绩：", validate_score)
        chemistry = get_valid_input("化学成绩：", validate_score)
        
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

def reset_sequence():
    """重置自增序列"""
    try:
        # 获取当前最大ID
        max_id = session.query(StudentScore).order_by(StudentScore.id.desc()).first()
        if max_id:
            from sqlalchemy import text
            try:
                # 先检查表是否存在
                session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"))
                # 如果表存在则更新
                session.execute(
                    text('UPDATE sqlite_sequence SET seq = :seq WHERE name = :name'),
                    {'seq': max_id.id, 'name': 'student_scores'}
                )
            except Exception:
                # 如果表不存在则跳过重置
                pass
            finally:
                session.commit()
    except Exception as e:
        print(f"重置序列失败: {e}")
        session.rollback()

def reorder_ids():
    """重新排序所有记录的ID"""
    try:
        # 获取所有记录并按ID排序
        students = session.query(StudentScore).order_by(StudentScore.id).all()
        
        # 重新设置ID
        for index, student in enumerate(students, start=1):
            student.id = index
            
        session.commit()
        print("记录重新排序完成")
    except Exception as e:
        print(f"重新排序失败: {e}")
        session.rollback()

def delete_student():
    """删除学生记录并重新排序"""
    try:
        student_id = get_valid_input("请输入要删除的学生ID：", int)
        # 使用新的 API 方法
        student = session.get(StudentScore, student_id)
        
        if student:
            session.delete(student)
            session.commit()
            
            # 重新排序剩余记录
            reorder_ids()
            
            # 重置自增序列
            reset_sequence()
            print(f"已删除ID为 {student_id} 的学生并重新排序")
        else:
            print("未找到该学生")
            
    except Exception as e:
        print(f"删除失败: {e}")
        session.rollback()

def print_menu():
    """打印菜单界面"""
    menu = """
=======================
    学生成绩管理系统
=======================

    1. 显示所有记录
    2. 添加新记录
    3. 删除记录
    4. 退出系统

=======================
"""
    print(menu)

# 初始化数据库连接
engine = create_engine('sqlite:///student.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    try:
        while True:
            try:
                print_menu()
                choice = get_valid_input("\n请选择操作(1-4): ")
                
                if choice == '1':
                    show_all()
                elif choice == '2':
                    add_student()
                elif choice == '3':
                    delete_student()
                elif choice == '4':
                    print("\n正在退出程序...")
                    break
                else:
                    print("无效的选择，请重新输入")
                    
            except ValueError as e:
                print(f"\n输入错误: {e}")
            except Exception as e:
                print(f"\n发生错误: {e}")
                
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    finally:
        print("\n正在关闭数据库连接...")
        session.close()
        print("程序已退出！")