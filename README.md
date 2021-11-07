Covid Monitor: http://ec2-54-202-56-60.us-west-2.compute.amazonaws.com/

# Pair Programming 
### Procedure
To kickstart our workflow we decided to start the assignment using pair programming over Zoom. In our first session on Monday (01/11/21) we first scanned the project requirements and discussed ideas. We continued to setup
our API project using Django and SQLite. Also, we implemented the models required to store the information read from the csv files and started work on the create function found in views.py to pass this data. During this
first session Natalia served as the driver actively writing code and Robin as the navigator responsible for reviewing code. 

On Tuesday (02/11/21) we inverted our approach and had Robin become the driver and Natalia the navigator. During this session the team continued work on the create method and began work on verifying csv files to check if
they followed one of the four formats from the GitHub on the assignment handout. To end the session, we held a brief discussion on how to efficiently divide tasks between ourselves. 

Starting from Wednesday (03/11/21) team members started to work on their designated tasks individually. When stuck or a major milestone was achieved that required the other's attention, we hosted more pair programming sessions. 
For instance, once one of us finished the basic unit testing functionality we had a quick meeting in which that person would be the navigator and explain to the driver how to implement tests for their code. Of course, the driver in
this scenario would write one or two tests while being guided by the supervisor. 


As you can see on the image of the commit activity below we only had one or two commits during our first to pair programming sessions but significantly more as we branched off to work individually using pair programming
only when needing help or when in a scenario as described previously. 

![alt text](https://github.com/csc301-fall-2021/assignment-2-1-robingerster-nataliamoran/blob/main/commit_activity.png?raw=true)

### Reflection
Some of the pros of pair programming include:
* By starting the assignment using a pair programming setup we easily established a common ground. That means, both team members were aware of the basic structures underlying the project (such as the models) before branching
off to start working individually. Clearly, this was extremely useful as no partner felt as though they were working with black box algorithms.

* By being in a voice chat during sessions we were also able to divide work between ourselves, establish expectations or bounce ideas off each other. For instance, while a driver was writing code to verify csv files the navigator
was able to think about the design. This made us move the csv verification code out of the views.py (where it did not belong) or use inheritance as a design principle when implementing the DailyWriter and SeriesWriter classes.

* By reconvening when milestones were met, we were able to save time as the team member who was not responsible for that milestone was quickly introduced to it and guided through it using a pair programming format. 

* One advantage of doing pair programming via Zoom was that we were able to save commute time. Also, by using screen sharing we always had a clear view of the driver's code which may not have been the case if we had to share a screen
in an in-person session.

Some of the cons include:
* Sometimes there were unforeseen circumstances with software related issues. For example, to use a Django server configuration in PyCharm one must own the professional licence. As one of us did not have this, some time
was lost when the navigator had to wait until this was resolved. 

* Pair programming required both partners to find a suitable time of day in which they can team up. Since both of us have busy schedules, this led to logistic challenges.

All in all, our team felt that pair programing was a positive experience and helped us save time. This could have been even more evident if logistic challenges could have been avoided.  

