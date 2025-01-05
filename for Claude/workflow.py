import streamlit as st
from SpiffWorkflow.specs import WorkflowSpec, Simple, StartTask
from SpiffWorkflow.workflow import Workflow
import graphviz

def create_workflow_spec():
    spec = WorkflowSpec()
    
    # Create a start task explicitly
    start = StartTask(spec)
    spec.start = start
    spec.task_specs['Start'] = start
    
    # Create tasks using Simple
    design = Simple(spec, 'Design Wall')
    spec.task_specs['Design Wall'] = design
    
    review = Simple(spec, 'Review Design')
    spec.task_specs['Review Design'] = review
    
    production = Simple(spec, 'Production')
    spec.task_specs['Production'] = production
    
    end = Simple(spec, 'End')
    spec.task_specs['End'] = end
    
    # Build the workflow by adding tasks
    start.connect(design)
    design.connect(review)
    review.connect(production)
    production.connect(end)
    
    return spec

def afficher_workflow():
    # Create workflow
    spec = create_workflow_spec()
    workflow = Workflow(spec)
    
    # Create graph
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')
    
    # Add nodes
    for task_spec in spec.task_specs.values():
        shape = 'circle' if task_spec.name in ['Start', 'End'] else 'box'
        dot.node(task_spec.name, task_spec.name, shape=shape)
        
        # Add edges
        if hasattr(task_spec, 'outputs'):
            for next_task in task_spec.outputs:
                dot.edge(task_spec.name, next_task.name)
    
    st.graphviz_chart(dot)

st.title("SpiffWorkflow Construction Process")
afficher_workflow()