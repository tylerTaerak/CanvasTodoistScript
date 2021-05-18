from canvasapi import Canvas
import todoist
import json
import logging
# TODO: make use of the logging library to add INFO markers when running the script, as well as any ERRORs
# Additionally, use a -v/--verbose and a -d/--debug marker to administrate this

class CanvasAutomate:
    def __init__(self, api_tokens='./json/access_tokens.json', rw_path='./json/info.json'):e
        try:
            with open(api_tokens) as handle:
                tokens = json.load(handle)

            if token['canvas-api-access'] == [] or tokens['todoist-api-access'] == '':
                raise Exception("check your credentials in the ./json/access_tokens.json file")
            self.cv = Canvas(tokens['canvas-api-access'][0], tokens['canvas-api-access'][1])
            self.td = todoist.TodoistAPI(tokens['todoist-api-access'])
            self.td.sync()
            self.write_path = rw_path
            with open(rw_path) as handle:
                self.info = json.load(handle)
        except FileNotFoundError as e:
            raise FileNotFoundError("check ./json/access_tokens.json or ./json/info.json")


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
    def add_course_projects(self):
        courses = self.current_courses
        for i in courses:
            if i.id in courses.keys():
                continue
            proj = self.td.projects.add(i.name, color=i.course_color)
            self.td.commit()
            self.info[i.id]['project_id'] = proj.id


    # Adds an assignment task to Todoist, then adds the assignment id to the info dict
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


    # Verifies whether an assignment task has already been made in Todoist
    # Returns False if the assignment has been made previously, and True otherwise
    def verify_asgn(self, course, asgn):
        course = self.info[course.id]
        if asgn.id in course['assignments']:
            return False
        return True


if __name__ == '__main__':
    import argparse
    cv = CanvasAutomate()
    del cv
