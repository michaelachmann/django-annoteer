from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import ImportForm
from projects.models import Project

import csv

def dataitem_import(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)

        if form.is_valid():

            # Reading File, Checking for CSV
            csv_file = form.cleaned_data['file']
            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())

            #TODO: Refactor to work with unique external_ids within projects!
            n_added, n_skipped = 0, 0
            for row in reader:
                try:
                    item = Dataitem.objects.create(project=project, created_by=request.user)
                    item.text = row['text']
                    item.external_id = row['id']
                    item.project = project
                    item.save()
                    n_added += 1

                except IntegrityError:
                    n_skipped += 1

            messages.success(request, f"Imported {n_added}, skipped {n_skipped}.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ImportForm()

    return render(request, "dataitem/dataitem_import.html", {'form': form})

def dataitem_list(request):
    dataitems = Dataitem.objects.all()
    return render(request, "dataitems/dataitem_list.html", {"dataitems": dataitems})


def dataitem_detail(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    return render(request, "dataitems/dataitem_detail.html", {"dataitem": dataitem})


# TODO: Reintroduce the form for creating a single Dataitem manually in the interface!
#@login_required
#def dataitem_create(request):
#    if request.method == "POST":
#        form = DataitemForm(request.POST)
#        if form.is_valid():
#            dataitem = form.save(commit=False)
#            dataitem.created_by = request.user
            # Optionally set project here if applicable
#            dataitem.save()
#            return redirect("dataitems:dataitem_list")
#    else:
#        form = DataitemForm()
#    return render(request, "dataitems/dataitem_form.html", {"form": form})


@login_required
def dataitem_update(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    form = DataitemForm(request.POST or None, instance=dataitem)
    if form.is_valid():
        form.save()
        return redirect("dataitems:dataitem_detail", pk=dataitem.pk)
    return render(request, "dataitems/dataitem_form.html", {"form": form})


@login_required
def dataitem_delete(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    if request.method == "POST":
        dataitem.delete()
        return redirect("dataitems:dataitem_list")
    return render(request, "dataitems/dataitem_confirm_delete.html", {"dataitem": dataitem})