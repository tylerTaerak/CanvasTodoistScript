from canvasapi import Canvas
import todoist
import json
import logging
# TODO: make use of the logging library to add INFO markers when running the script, as well as any ERRORs
# Additionally, use a -v/--verbose and a -d/--debug marker to administrate this

class CanvasAutomate:
    def __init__(self, api_tokens='./json/access_tokens.json', rw_path='./json/info.json'):
        with open(api_tokens) as handle:
            tokens = json.load(handle)

        self.cv = Canvas(tokens['canvas-api-access'][0], tokens['canvas-api-access'][1])
        self.td = todoist.TodoistAPI(tokens['todoist-api-access'])
        self.td.sync()
        self.write_path = rw_path
        with open(rw_path) as handle:
            self.info = json.load(handle)


    def __del__(self):
        with open(self.write_path, 'w') as handle:
            json.dump(self.info, handle)


    # the top level function of the class, which will handle all the adding of assignments to the todo list
    def do_the_thing(self):
        self.add_course_projects()
        for i in self.current_courses:
            for j in i.get_assignments():
                self.add_asgn(i, j)


    # returns a list of names of courses taken during the semester (marked as favorites
    # in Canvas)
    #
    # Likely will not be used outside of other class methods, but is listed as a property
    # for help and debugging, may be used for logging in the future

    @property 
    def current_courses(self):
        return self.cv.get_current_user().get_favorite_courses()
        

    # does not return anything, but adds new Todoist projects for each favorite course
    # Adds the ids of these new projects in the info dict under the course id
    # TODO: add a check to make sure the course is not already a project in Todoist
    def add_course_projects(self):
        courses = self.current_courses
        for i in courses:
            proj = self.td.projects.add(i.name, color=i.course_color)
            self.td.commit()
            self.info[i.id]['project_id'] = proj.id


    def add_asgn(self, course, asgn):
        if not verify_asgn(self.verify_asgn(course, asgn):
            return False
        prj = self.info[course.id]['project_id']
        strf = assgn.due_at.strftime('%b %d')
        if assgn.due_at.hour != 11 and assgn.due_at.minute != 59:
            strf += assgn.due_at.strftime(' %I:%M %p')
        self.td.items.add(asgn.name, due={'string': strf}, project_id=prj, description=asgn.id)
        self.info[course.id]['assignments'].append(asgn.id)
        return True


    def verify_asgn(self, course, asgn):
        course = self.info[course.id]
        if asgn.id in course['assignments']:
            return True
        return False


if __name__ == '__main__':
    import argparse
    cv = CanvasAutomate()
    del cv
