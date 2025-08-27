from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import DataitemForm, CSVUploadForm
import io
import csv
from django.shortcuts import redirect
from projects.models import Project


def dataitem_list(request):
    dataitems = Dataitem.objects.all()
    project = Project.objects.first()
    return render(request, "dataitems/dataitem_list.html", {
        "dataitems": dataitems,
        "project": project
    })

def dataitem_detail(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    return render(request, "dataitems/dataitem_detail.html", {"dataitem": dataitem})

'''
@login_required
create function no longer needed because of import-function
def dataitem_create(request):
    if request.method == "POST":
        form = DataitemForm(request.POST)
        if form.is_valid():
            dataitem = form.save(commit=False)
            dataitem.created_by = request.user
             Optionally set project here if applicable
            dataitem.save()
            return redirect("dataitems:dataitem_list")
    else:
        form = DataitemForm()
    return render(request, "dataitems/dataitem_form.html", {"form": form})
'''


@login_required()
def dataitem_import(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        pasted_data = request.POST.get('pasted_data', '').strip()
        print("Pasted text:", pasted_data)

        rows = []

        #CSV-Datei verarbeiten, falls vorhanden
        if form.is_valid() and form.cleaned_data.get('file'):
            file = form.cleaned_data['file']
            try:
                decoded_file = io.TextIOWrapper(file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)

                if 'id' not in reader.fieldnames or 'text' not in reader.fieldnames:
                    form.add_error('file', 'CSV muss Spalten "id" und "text" enthalten.')
                    return render(request, 'dataitems/dataitem_import.html', {'form': form, 'project': project})
                for row in reader:
                    rows.append({'id': row['id'].strip(), 'text': row['text'].strip()})
            except UnicodeDecodeError:
                form.add_error("file", "Datei konnte nicht als UTF-8 gelesen werden")
                return render(request, 'dataitems/dataitem_import.html', {'form': form, 'project': project})


        #Copy-Paste-Data verarbeiten, falls vorhanden
        elif pasted_data:
            lines = pasted_data.splitlines()
            for line in lines:
                if '\t' in line:
                    parts = line.split('\t')
                elif ',' in line:
                    parts = line.split(',', 1)
                elif ';' in line:
                    parts = line.split(';', 1)
                else:
                    parts = []

                if len(parts) >= 2:
                    rows.append({'id': parts[0].strip(), 'text': parts[1].strip()})
                else:
                    messages.warning(request, f"Skipped row (non compatible format): {line}")

        #Daten speichern
        existing_ids = set(Dataitem.objects.filter(project=project).values_list('external_id', flat=True))
        items_to_create = []
        count_created = 0
        count_updated = 0

        for row in rows:
            external_id = row['id'].strip()
            text = row['text'].strip()
            if external_id in existing_ids:
                Dataitem.objects.filter(external_id=external_id, project=project).update(text=text)
                count_updated += 1
            else:
                items_to_create.append(Dataitem(
                    external_id=external_id,
                    text=text,
                    created_by=request.user,
                    project=project
                ))
                count_created += 1


        print("Received rows:", rows)
        print("Existing IDs:", existing_ids)
        print("Items to be created:", items_to_create)

        Dataitem.objects.bulk_create(items_to_create, ignore_conflicts=True)

        return render(request, 'dataitems/data_import_success.html', {
            'created': count_created,
            'updated': count_updated,
            'project': project,
        })

    else:
        form = CSVUploadForm()

    return render(request, 'dataitems/dataitem_import.html', {'form': form, 'project': project})


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
    project = getattr(dataitem, 'project', None)

    if request.method == "POST":
        dataitem.delete()
        if project:
            return redirect("projects:project_detail", pk=project.pk)
        else:
            return redirect("dataitems:dataitem_list")

    return render(request, "dataitems/dataitem_confirm_delete.html", {
        "dataitem": dataitem,
        "project": project
    })