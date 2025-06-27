# projects/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from dataitem.models import Dataitem
from .models import Project, Label
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, LabelForm

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

def import_csv(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return HttpResponse(f"This is where CSV import for project '{project.name}' will happen.")

@login_required
def label_management(request, pk):
    project = get_object_or_404(Project, pk=pk)
    labels = project.label_set.all()

    if request.method == "POST":
        form = LabelForm(request.POST, project=project)
        if form.is_valid():
            label = form.save(commit=False)
            label.project = project
            label.save()

            # Check which button was clicked
            action = request.POST.get("action")
            if action == "create_and_exit":
                # Redirect to Project Detail page
                return redirect("projects:project_detail", pk=project.pk)
            else:
                # Default: stay on label management page
                return redirect("projects:label_management", pk=project.pk)
    else:
        form = LabelForm(project=project)

    return render(request, "projects/project_label.html", {
        "project": project,
        "labels": labels,
        "form": form,
    })

@login_required
def project_labels_bulk(request, pk):
    project = get_object_or_404(Project, pk=pk)

    LabelFormSet = inlineformset_factory(
        Project,
        Label,
        form=LabelForm,
        fields=("label", "value"),
        extra=3,
        can_delete=True
    )

    if request.method == "POST":
        formset = LabelFormSet(request.POST, instance=project)
        if formset.is_valid():
            formset.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        formset = LabelFormSet(instance=project)

    return render(request, "projects/label_formset.html", {
        "project": project,
        "formset": formset,
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