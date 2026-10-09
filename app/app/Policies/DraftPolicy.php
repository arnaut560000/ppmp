<?php
namespace App\Policies;
use App\Models\{User,Draft};
class DraftPolicy {
    public function view(User $user,Draft $draft): bool {
        return $user->department_id !== null && (int)$user->department_id === (int)$draft->department_id;
    }
    public function update(User $user,Draft $draft): bool { return $this->view($user,$draft); }
}
