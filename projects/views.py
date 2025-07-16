from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.forms import inlineformset_factory

from .models import Project, Label
from .forms import ProjectForm, LabelForm

from dataitem.models import Dataitem, DataBatch

import csv
from io import TextIOWrapper

def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    dataitems = Dataitem.objects.filter(project=project)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "dataitems": dataitems,
    })

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            # redirect to label management for this project
            return redirect("projects:label_management", project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form})


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:label_management", project.pk)
    return render(request, "projects/project_form.html", {"form": form})



@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})



@login_required
def project_instructions(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.instructions()
        return redirect("projects:project_list")
    return render(request, "projects/project_instructions.html", {"project": project})




@login_required
def label_management(request, pk):
    project = get_object_or_404(Project, pk=pk)
    labels = project.label_set.all()

    if request.method == "POST":
        action = request.POST.get("action")
        form = LabelForm(request.POST, project=project)

        if action == "create_and_exit":
            # If any field was filled, validate and save
            if any(request.POST.get(field) for field in form.fields):
                # Check for duplicates
                if project.label_set.filter(value=form.data.get("value")).exists():
                    messages.error(request, "A label with this value already exists in this project.")
                    return redirect("projects:project_detail", pk=project.pk)

                if form.is_valid():
                    label = form.save(commit=False)
                    label.project = project
                    label.save()
            # Redirect regardless
            return redirect("projects:project_detail", pk=project.pk)

        # Default action (create and stay)
        # Check for duplicates
        if project.label_set.filter(value=form.data.get("value")).exists():
            form.add_error("value", "A label with this value already exists in this project.")
            return render(request, "projects/project_label.html", {
                "project": project,
                "labels": labels,
                "form": form,
            })

        if form.is_valid():
            label = form.save(commit=False)
            label.project = project
            label.save()
            return redirect("projects:label_management", pk=project.pk)

    else:
        form = LabelForm(project=project)

    return render(request, "projects/project_label.html", {
        "project": project,
        "labels": labels,
        "form": form,
    })
@login_required
def label_edit(request, pk):
    label = get_object_or_404(Label, pk=pk)
    project = label.project

    if request.method == "POST":
        form = LabelForm(request.POST, instance=label, project=project)
        if form.is_valid():
            form.save()
            return redirect("projects:label_management", pk=project.pk)
    else:
        form = LabelForm(instance=label, project=project)

    return render(request, "projects/label_form.html", {
        "form": form,
        "project": project,
        "label": label,
    })

@login_required
def label_delete(request, pk):
    label = get_object_or_404(Label, pk=pk)
    project = label.project

    if request.method == "POST":
        label.delete()
        return redirect("projects:label_management", pk=project.pk)

    return render(request, "projects/label_confirm_delete.html", {
        "label": label,
        "project": project,
    })
def next_dataitem(project, user):
    """
    Returns the next DataItem:
    - with less than project.num_annotators annotations
    - not yet annotated by this user
    """
    return (
        Dataitem.objects
        .filter(project=project)
        .annotate(
            total=Count('annotations', distinct=True),
            mine=Count(
                'annotations',
                filter=Q(annotations__annotator=user),
                distinct=True
            )
        )
        .filter(total__lt=project.num_annotators, mine=0)
        .order_by('total', 'pk')
        .first()
    )




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from dataitem.models import Dataitem, Annotation, AnnotationLabel
from .models import Project

def next_dataitem(project, user):
    return (
        Dataitem.objects
        .filter(project=project)
        .annotate(
            total=Count('annotations', distinct=True),
            mine=Count(
                'annotations',
                filter=Q(annotations__annotator=user),
                distinct=True
            )
        )
        .filter(total__lt=project.num_annotators, mine=0)
        .order_by('total', 'pk')
        .first()
    )

@login_required
def annotate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    dataitem = next_dataitem(project, request.user)

    # Count total needed annotations
    total_items = Dataitem.objects.filter(project=project).count()
    total_needed = total_items * project.num_annotators

    # Count how many this user has done
    annotated_by_user = Annotation.objects.filter(
        dataitem__project=project,
        annotator=request.user
    ).count()

    # Calculate progress percentage
    progress_percent = (
        (annotated_by_user / total_needed * 100)
        if total_needed > 0 else 0
    )

    if not dataitem:
        return render(request, "projects/annotate.html", {
            "project": project,
            "dataitem": None,
            "total_needed": total_needed,
            "annotated_by_user": annotated_by_user,
            "progress_percent": progress_percent,
        })

    if request.method == "POST":
        selected_labels = request.POST.getlist("labels")
        if selected_labels:
            annotation = Annotation.objects.create(
                dataitem=dataitem,
                annotator=request.user
            )
            for label_id in selected_labels:
                AnnotationLabel.objects.create(
                    annotation=annotation,
                    label_id=label_id
                )
        return redirect("projects:project_annotate", pk=project.pk)

    return render(request, "projects/annotate.html", {
        "project": project,
        "dataitem": dataitem,
        "total_needed": total_needed,
        "annotated_by_user": annotated_by_user,
        "progress_percent": progress_percent,
    })

@login_required
def project_export(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Permission check
    if request.user != project.created_by:
        return HttpResponseForbidden("You do not have permission to export this project's annotations.")


    # Get all annotators
    annotators = User.objects.filter(
        annotations__dataitem__project=project
    ).distinct().order_by("username")



    # Prepare CSV response
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response.write("\ufeff")  # Write UTF-8 BOM for Excel compatibility


    response["Content-Disposition"] = f'attachment; filename="project_{project.pk}_annotations.csv"'

    writer = csv.writer(response)
    header = ["external_id", "text"] + [user.username for user in annotators]
    writer.writerow(header)

    #for testing only:
    # Get all DataItems in the project
    dataitems = Dataitem.objects.filter(project=project).prefetch_related(
        "annotations__labels__label",
        "annotations__annotator"
    )
    for item in dataitems:
        row = [item.external_id, item.text]

        for user in annotators:
            # Get the annotation by this user, if any
            annotation = next(
                (a for a in item.annotations.all() if a.annotator_id == user.id),
                None
            )

            if annotation:
                # Get label values
                label_values = [l.label.value for l in annotation.labels.all()]
                if project.label_type == "SI":
                    value = label_values[0] if label_values else ""
                else:
                    value = ";".join(label_values)
            else:
                value = ""

            row.append(value)

        writer.writerow(row)

    return response






