import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';   

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private baseUrl = 'http://127.0.0.1:8000/core/v1';

  constructor(private http: HttpClient) { } 

  login(credentials: { email: string, password: string , role: string}) {
    return this.http.post(`${this.baseUrl}/auth/login/`, credentials);
  }

  registerStudent(data: any) {
    return this.http.post(`${this.baseUrl}/admin/register/`, data);
  }

  getStudents() {
    return this.http.get(`${this.baseUrl}/students/`);
  }

}