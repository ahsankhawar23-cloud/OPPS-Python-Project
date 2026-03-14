# IN this program, sudents are given grades on the basis of their marks.

# 1. I learned how to use @dataclass in Python.
# 2. I learned how to use private variables using double underscore (__).
# 3. I learned how to validate user input.
# 4. I understood how dictionaries store subject and marks.
# 5. I learned how to calculate averages safely.
# 6. I learned how to use Optional and Tuple from typing.
# 7. I understood how to raise errors like ValueError and KeyError.
# 8. I learned how to find subject topper and overall topper.
# 9. I learned how to build a menu-driven CLI program.
# 10. I improved my understanding of Object-Oriented Programming (OOop)

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional


@dataclass
class Student:
    student_id: str
    name: str
    __marks: Dict[str, float] = field(default_factory=dict, repr=False)

    def set_mark(self, subject: str, score: float) -> None:
        subject = subject.strip()
        if not subject:
            raise ValueError("Subject cannot be empty.")
        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100.")
        self.__marks[subject] = score

    def get_mark(self, subject: str) -> Optional[float]:
        return self.__marks.get(subject)

    def average(self) -> float:
        return sum(self.__marks.values()) / len(self.__marks) if self.__marks else 0.0

    @property
    def marks(self) -> Dict[str, float]:
        return dict(self.__marks)  # return copy

    def report_lines(self) -> list[str]:
        lines = [f"Student: {self.student_id} - {self.name}"]
        if not self.__marks:
            lines.append("No marks recorded.")
            return lines

        for subject, score in sorted(self.__marks.items()):
            lines.append(f"- {subject}: {score}")
        lines.append(f"Average: {self.average():.2f}")
        return lines


class Gradebook:
    def __init__(self):
        self.students: Dict[str, Student] = {}
    def add_student(self, student_id: str, name: str) -> None:
        student_id = student_id.strip()
        name = name.strip()

        if not student_id or not name:
            raise ValueError("Student ID and name are required.")
        if student_id in self.students:
            raise ValueError("Student ID already exists.")

        self.students[student_id] = Student(student_id, name)

    def record_mark(self, student_id: str, subject: str, score: float) -> None:
        if student_id not in self.students:
            raise KeyError("Student not found.")
        self.students[student_id].set_mark(subject, score)

    def student_report(self, student_id: str) -> list[str]:
        if student_id not in self.students:
            raise KeyError("Student not found.")
        return self.students[student_id].report_lines()

    def subject_topper(self, subject: str) -> Tuple[str, float]:
        topper_id = ""
        topper_score = -1.0

        for sid, st in self.students.items():
            score = st.get_mark(subject)
            if score is not None and score > topper_score:
                topper_score = score
                topper_id = sid

        if topper_score < 0:
            raise ValueError("No marks found for this subject.")

        return topper_id, topper_score

    def overall_topper(self) -> Tuple[str, float]:
        if not self.students:
            raise ValueError("No students.")

        best_id = ""
        best_avg = -1.0

        for sid, st in self.students.items():
            avg = st.average()
            if avg > best_avg:
                best_avg = avg
                best_id = sid

        return best_id, best_avg


def main():
    gb = Gradebook()

    while True:
        print("\n--- Gradebook Menu ---")
        print("1) Add student")
        print("2) Record/Update mark")
        print("3) Show student report")
        print("4) Subject topper")
        print("5) Overall topper")
        print("6) Exit")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                sid = input("Student ID: ")
                name = input("Name: ")
                gb.add_student(sid, name)
                print("Student added.")

            elif choice == "2":
                sid = input("Student ID: ")
                subject = input("Subject: ")
                score = float(input("Score (0-100): "))
                gb.record_mark(sid, subject, score)
                print("Mark recorded.")

            elif choice == "3":
                sid = input("Student ID: ")
                for line in gb.student_report(sid):
                    print(line)

            elif choice == "4":
                subject = input("Subject: ")
                sid, score = gb.subject_topper(subject)
                st = gb.students[sid]
                print(f"Topper: {st.name} ({sid}) with {score}")

            elif choice == "5":
                sid, avg = gb.overall_topper()
                st = gb.students[sid]
                print(f"Overall topper: {st.name} ({sid}) average {avg:.2f}")

            elif choice == "6":
                print("Goodbye.")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()