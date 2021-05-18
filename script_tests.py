import unittest
from canvas_script import CanvasAutomate

class TestCanvasScript(unittest.TestCase):

    def test_currentCourseNames(self):
        cv = CanvasAutomate('./access_tokens.json')
        courses = [x.name for x in cv.current_courses]
        self.assertTrue('ECE Advising' in courses) 

    # I should figure out a good way to do the assertion that's a little more scalable
    def test_addCourseProjects(self):
        cv = CanvasAutomate('./access_tokens.json')
        cv.add_course_projects()
        td_proj_names = [x['name'] for x in cv.td.state['projects']]
        self.assertTrue('ECE Advising' in td_proj_names)

if __name__ == '__main__':
    unittest.main()
