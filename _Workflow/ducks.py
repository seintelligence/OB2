import streamlit as st
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.task import Task
from SpiffWorkflow.specs.base import TaskSpec

def init_workflow():
    if 'workflow' not in st.session_state:
        parser = BpmnParser()
        parser.add_bpmn_file('ducks.bpmn')
        spec = parser.get_spec('duck_process')
        st.session_state.workflow = BpmnWorkflow(spec)
        st.session_state.workflow.do_engine_steps()

def show_form(task):
    form = task.task_spec.form
    task_data = {}
    
    if hasattr(form, 'fields'):
        for field in form.fields:
            if field.type == "boolean":
                answer = st.checkbox(field.label, key=f"field_{field.id}")
            elif hasattr(field, 'options'):  # For enum fields
                options = [option.id for option in field.options]
                answer = st.selectbox(field.label, options, key=f"field_{field.id}")
            elif field.type == "long":
                answer = st.number_input(field.label, key=f"field_{field.id}")
            else:
                answer = st.text_input(field.label, key=f"field_{field.id}")
            
            task_data[field.id] = answer
    
    return task_data

def main():
    st.title("BPMN Workflow Interface")
    
    # Initialize workflow
    init_workflow()
    
    # Get current task
    next_task = st.session_state.workflow.get_next_task()
    
    if next_task is not None:
        st.header(f"Current Task: {next_task.task_spec.name}")
        
        if hasattr(next_task.task_spec, 'form'):
            task_data = show_form(next_task)
            
            if st.button("Complete Task"):
                for key, value in task_data.items():
                    next_task.update_data_var(key, value)
                next_task.complete()
                st.session_state.workflow.do_engine_steps()
                st.rerun()
        else:
            st.write("This is a system task.")
            if st.button("Complete Task"):
                next_task.complete()
                st.session_state.workflow.do_engine_steps()
                st.rerun()
                
        # Show current workflow data
        st.subheader("Current Workflow Data")
        st.json(next_task.data)
        
    else:
        st.success("Workflow completed!")
        
        # Add reset button
        if st.button("Restart Workflow"):
            del st.session_state.workflow
            st.rerun()
            
    # Show workflow progress
    st.subheader("Workflow Progress")
    all_tasks = st.session_state.workflow.get_tasks()
    
    # Debug information
    st.write("Available task states:")
    for task in all_tasks:
        st.write(f"Task: {task.task_spec.name}, State: {task.state}")
    
    # Use task.state to filter completed tasks
    completed_tasks = [task for task in all_tasks if task.state > 0]  # Assuming completed tasks have state > 0
    
    if all_tasks:
        progress = len(completed_tasks) / len(all_tasks)
        st.progress(progress)
        st.write(f"Completed {len(completed_tasks)} of {len(all_tasks)} tasks")
    
    # Show task history
    st.subheader("Task History")
    for task in completed_tasks:
        with st.expander(f"Task: {task.task_spec.name}"):
            st.write("Task Data:", task.data)
            st.write("State:", task.state)

if __name__ == "__main__":
    main()