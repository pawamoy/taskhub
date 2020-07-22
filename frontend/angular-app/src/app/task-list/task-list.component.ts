import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Observable } from 'rxjs';

import { ApiService } from '../api.service';
import { Task } from '../task';

@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.component.html',
  styleUrls: ['./task-list.component.css']
})
export class TaskListComponent implements OnInit {
  tasks$: Observable<Task[]>;
  task_form: FormGroup;

  constructor(private apiService: ApiService, private form_builder: FormBuilder) { }

  ngOnInit() {
    this.getTasks();

    this.task_form = this.form_builder.group({
          title: "",
          description: "",
          priority: 50,
          confidential: false
    });

    this.task_form.controls["title"].setValidators([Validators.required]);
    this.task_form.controls["description"].setValidators([Validators.required]);
  }

  public getTasks() {
    this.tasks$ = this.apiService.getTasks();
  }

  onSubmit() {
    this.apiService.postTask(this.task_form.value)
      .subscribe(
        (response) => {
          console.log(response);
          this.getTasks();
        }
      )
  }

  deleteTask(task_id: number) {
    this.apiService.deleteTask(task_id)
      .subscribe(
        (response) => {
          console.log(response);
          this.getTasks();
        }
      )
  }

  updateTask(task) {
    this.apiService.putTask(task)
      .subscribe(
        (response) => {
          console.log(response);
          this.getTasks();
        }
      )
  }

}
