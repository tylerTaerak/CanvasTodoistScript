from canvasapi import Canvas
from todoist import TodoistAPI
import json
from pytz import timezone
import logging


logging.basicConfig(level=logging.WARNING)
# TODO: make use of the logging library to add INFO markers when running the script, as well as any ERRORs
# Additionally, use a -v/--verbose and a -d/--debug marker to administrate this

class CanvasAutomate:
    def __init__(self, 
            api_tokens='./json/access_tokens.json', 
            rw_path='./json/info.json', 
            verbose=False, 
            debug=False):
        try:
            with open(api_tokens) as handle:
                tokens = json.load(handle)

            if tokens['canvas-api-access'] == [] or tokens['todoist-api-access'] == '':
                raise Exception("check your credentials in the ./json/access_tokens.json file")
            self.cv = Canvas(tokens['canvas-api-access'][0], tokens['canvas-api-access'][1])
            self.td = TodoistAPI(tokens['todoist-api-access'])
            self.td.sync()
            self.write_path = rw_path

            if verbose:
                logging.basicConfig(level=logging.INFO)
            if debug:
                logging.basicConfig(level=logging.DEBUG)

            with open(rw_path, 'r') as handle:
                self.info = json.load(handle)

        except FileNotFoundError as e:
            raise FileNotFoundError("check ./json/access_tokens.json or ./json/info.json")


    def __del__(self):
        logging.info('Finishing up...')
        try:
            self.td.commit()
            print('Changes committed to Todoist')
            with open(self.write_path, 'w') as handle:
                json.dump(self.info, handle)
        except Exception:
            print('deleted without saving info')
        logging.info('Complete. Deleting CanvasAutomate Object')
        print('Script Complete.')


    # the top level function of the class, which will handle all the adding of assignments to the todo list
    def add_all_assignments_to_todoist(self):
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
            if str(i.id) in self.info.keys():
                proj_lst = [x['id'] for x in self.td.state['projects']]
                if self.info[str(i.id)]['project_id'] in proj_lst:
                    continue
            logging.info(f'Adding Course: {i.name}')
            print(f'Adding Course: {i.name}')
            self.info[str(i.id)] = {'assignments': []}
            proj = self.td.projects.add(i.name, color=i.course_color)
            self.td.commit()
            self.info[str(i.id)]['project_id'] = proj['id']
            logging.info(f'Course: {i.name} added')
            print(f'Course: {i.name} added')


    # Adds an assignment task to Todoist, then adds the assignment id to the info dict
    def add_asgn(self, course, asgn):
        if not self.verify_asgn(course, asgn):
            print(f'Assignment {asgn.name} already added to Todoist (id: {asgn.id})')
            return False
        logging.info(f'adding Assignment: {asgn.name}')
        print(f'Adding Assignment: {asgn.name}')
        prj = self.info[str(course.id)]['project_id']
        strf = None
        if asgn.due_at is not None:
            new_datetime = asgn.due_at_date.astimezone(timezone('US/Mountain'))
            strf = new_datetime.strftime('%b %d')
            if new_datetime.hour != 23 and new_datetime.minute != 59:
                strf += new_datetime.strftime(' %I:%M %p')
        url = ''
        if asgn.html_url is not None:
            url = asgn.html_url
        self.td.items.add(asgn.name, due={'string': strf}, project_id=prj, description=url)
        self.info[str(course.id)]['assignments'].append(asgn.id)
        logging.info(f'Assignment: {asgn.name} added')
        print(f'Assignment: {asgn.name} added')
        return True


    # Verifies whether an assignment task has already been made in Todoist
    # Returns False if the assignment has been made previously, and True otherwise
    def verify_asgn(self, course, asgn):
        course = self.info[str(course.id)]
        if asgn.id in course['assignments']:
            return False
        return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Transfer Canvas Assignments to Todoist')
    parser.add_argument('--access_tokens', dest='api_access', default='./json/access_tokens.json')
    parser.add_argument('--info_file', dest='info_file', default='./json/info.json')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true')
    args = parser.parse_args()

    cv = CanvasAutomate(api_tokens=args.api_access, rw_path=args.info_file, verbose=args.verbose, debug=args.debug)
    cv.add_all_assignments_to_todoist()

    del cv
