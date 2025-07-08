# projects/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from dataitem.models import Dataitem
from .models import Project, Label
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, LabelForm
from django.db.models import Count, Q
from dataitem.models import Dataitem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
import csv
from io import TextIOWrapper

from .models import Project
from dataitem.models import DataBatch
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



